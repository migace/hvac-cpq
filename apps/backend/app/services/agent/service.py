"""AgentService — orchestrates the LLM conversation with tool-calling loop.

Architecture:
  1. Receives user message + conversation history.
  2. Sends messages to OpenAI with tool definitions.
  3. If the model requests tool calls, executes them via AgentTools and loops.
  4. Streams partial text responses back to the caller via an async generator.
  5. Logs every step with structured observability (tokens, latency, cost, tools used).

The service is stateless — conversation history is managed by the caller.
"""

from __future__ import annotations

import json
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

import openai
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.agent.tool_definitions import TOOL_DEFINITIONS
from app.services.agent.tools import AgentTools

logger = get_logger()

SYSTEM_PROMPT = """\
You are an expert HVAC product advisor for a CPQ (Configure, Price, Quote) system.

Your role:
- Help users find the right HVAC products (fire dampers) based on their requirements.
- Search the product database using your tools — never guess product data.
- Provide accurate pricing, technical specifications, and order codes.
- Recommend valid configurations and explain business rules.

Behavior guidelines:
- Always use tools to look up real data. Do not fabricate product information.
- When a user describes what they need, use search_products first to find matching families.
- After finding a match, use get_family_details to learn about attributes, rules, and pricing.
- When the user provides enough parameters, calculate price and generate order code.
- If a configuration is invalid, explain why and suggest a valid alternative.
- Be concise and professional. Use tables or lists for structured data.
- When you have a complete recommendation, include a JSON block with the suggested \
configuration so the frontend can auto-fill the form. Format it as:

```json:suggested_configuration
{
  "family_id": <id>,
  "family_code": "<code>",
  "values": {
    "<attribute_code>": <value>,
    ...
  }
}
```

Respond in the same language the user writes in.
"""

MAX_TOOL_ITERATIONS = 10

# Approximate cost per 1M tokens for gpt-4.1-nano (as of 2025)
COST_PER_1M_INPUT_TOKENS = 0.10
COST_PER_1M_OUTPUT_TOKENS = 0.40


@dataclass
class ToolCallRecord:
    """Record of a single tool call for observability."""

    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    duration_ms: float


@dataclass
class AgentInvocationMetrics:
    """Metrics collected during a single agent invocation."""

    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    llm_calls: int = 0
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    total_duration_ms: float = 0.0
    estimated_cost_usd: float = 0.0


class AgentService:
    def __init__(self, session: Session) -> None:
        self.settings = get_settings()
        self.tools = AgentTools(session)
        self.model = self.settings.openai_model

        if not self.settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured. Set it in .env to enable the AI agent."
            )

        self.client = openai.OpenAI(api_key=self.settings.openai_api_key)

    async def chat_stream(
        self,
        *,
        messages: list[dict[str, Any]],
        conversation_id: str,
    ) -> AsyncGenerator[str, None]:
        """Run the agentic loop and yield SSE-formatted events.

        Event types:
          - data: {"type": "delta", "content": "..."}   — streamed text chunk
          - data: {"type": "tool_call", "name": "...", "arguments": {...}}  — tool call notification
          - data: {"type": "tool_result", "name": "...", "result": {...}}   — tool call result
          - data: {"type": "done", "metrics": {...}}     — final metrics
          - data: {"type": "error", "message": "..."}    — error
        """
        start_time = time.monotonic()
        metrics = AgentInvocationMetrics(model=self.model)

        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]

        logger.info(
            "agent_invocation_start",
            conversation_id=conversation_id,
            model=self.model,
            message_count=len(messages),
        )

        try:
            for _iteration in range(MAX_TOOL_ITERATIONS):
                metrics.llm_calls += 1

                stream = self.client.chat.completions.create(  # type: ignore[call-overload]
                    model=self.model,
                    messages=full_messages,
                    tools=TOOL_DEFINITIONS,
                    stream=True,
                    stream_options={"include_usage": True},
                )

                assistant_content = ""
                tool_calls_accumulator: dict[int, dict[str, Any]] = {}
                finish_reason = None

                for chunk in stream:
                    if chunk.usage:
                        metrics.input_tokens += chunk.usage.prompt_tokens
                        metrics.output_tokens += chunk.usage.completion_tokens
                        metrics.total_tokens += chunk.usage.total_tokens

                    if not chunk.choices:
                        continue

                    choice = chunk.choices[0]
                    finish_reason = choice.finish_reason or finish_reason

                    if choice.delta.content:
                        assistant_content += choice.delta.content
                        yield _sse_event("delta", {"content": choice.delta.content})

                    if choice.delta.tool_calls:
                        for tc in choice.delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_calls_accumulator:
                                tool_calls_accumulator[idx] = {
                                    "id": tc.id or "",
                                    "name": tc.function.name or "" if tc.function else "",
                                    "arguments": "",
                                }
                            if tc.id:
                                tool_calls_accumulator[idx]["id"] = tc.id
                            if tc.function:
                                if tc.function.name:
                                    tool_calls_accumulator[idx]["name"] = tc.function.name
                                if tc.function.arguments:
                                    tool_calls_accumulator[idx]["arguments"] += (
                                        tc.function.arguments
                                    )

                if finish_reason != "tool_calls" or not tool_calls_accumulator:
                    break

                assistant_message: dict[str, Any] = {
                    "role": "assistant",
                    "content": assistant_content or None,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": tc["arguments"],
                            },
                        }
                        for tc in tool_calls_accumulator.values()
                    ],
                }
                full_messages.append(assistant_message)

                for tc in tool_calls_accumulator.values():
                    tool_name = tc["name"]
                    try:
                        tool_args = json.loads(tc["arguments"])
                    except json.JSONDecodeError:
                        tool_args = {}

                    yield _sse_event("tool_call", {"name": tool_name, "arguments": tool_args})

                    tool_start = time.monotonic()
                    tool_result = self._execute_tool(tool_name, tool_args)
                    tool_duration_ms = (time.monotonic() - tool_start) * 1000

                    metrics.tool_calls.append(
                        ToolCallRecord(
                            name=tool_name,
                            arguments=tool_args,
                            result=tool_result,
                            duration_ms=round(tool_duration_ms, 2),
                        )
                    )

                    yield _sse_event("tool_result", {"name": tool_name, "result": tool_result})

                    full_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": json.dumps(tool_result),
                        }
                    )

                    logger.info(
                        "agent_tool_executed",
                        conversation_id=conversation_id,
                        tool=tool_name,
                        duration_ms=round(tool_duration_ms, 2),
                    )

            metrics.total_duration_ms = round((time.monotonic() - start_time) * 1000, 2)
            metrics.estimated_cost_usd = round(
                (metrics.input_tokens * COST_PER_1M_INPUT_TOKENS / 1_000_000)
                + (metrics.output_tokens * COST_PER_1M_OUTPUT_TOKENS / 1_000_000),
                6,
            )

            logger.info(
                "agent_invocation_complete",
                conversation_id=conversation_id,
                model=metrics.model,
                llm_calls=metrics.llm_calls,
                input_tokens=metrics.input_tokens,
                output_tokens=metrics.output_tokens,
                total_tokens=metrics.total_tokens,
                tool_calls_count=len(metrics.tool_calls),
                tools_used=[tc.name for tc in metrics.tool_calls],
                total_duration_ms=metrics.total_duration_ms,
                estimated_cost_usd=metrics.estimated_cost_usd,
            )

            yield _sse_event(
                "done",
                {
                    "metrics": {
                        "model": metrics.model,
                        "input_tokens": metrics.input_tokens,
                        "output_tokens": metrics.output_tokens,
                        "total_tokens": metrics.total_tokens,
                        "llm_calls": metrics.llm_calls,
                        "tool_calls_count": len(metrics.tool_calls),
                        "tools_used": [tc.name for tc in metrics.tool_calls],
                        "total_duration_ms": metrics.total_duration_ms,
                        "estimated_cost_usd": metrics.estimated_cost_usd,
                    }
                },
            )

        except openai.APIError as exc:
            logger.error(
                "agent_openai_error",
                conversation_id=conversation_id,
                error=str(exc),
                error_type=type(exc).__name__,
            )
            yield _sse_event("error", {"message": f"OpenAI API error: {exc.message}"})

        except Exception as exc:
            logger.exception(
                "agent_unexpected_error",
                conversation_id=conversation_id,
                error=str(exc),
            )
            yield _sse_event("error", {"message": "An unexpected error occurred."})

    def _execute_tool(self, name: str, arguments: dict[str, Any]) -> dict:
        tool_map = {
            "search_products": self.tools.search_products,
            "get_family_details": self.tools.get_family_details,
            "calculate_price": self.tools.calculate_price,
            "validate_configuration": self.tools.validate_configuration,
            "generate_order_code": self.tools.generate_order_code,
            "calculate_technical_params": self.tools.calculate_technical_params,
        }

        handler = tool_map.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}

        try:
            return handler(**arguments)  # type: ignore[operator]
        except Exception as exc:
            logger.warning("agent_tool_error", tool=name, error=str(exc))
            return {"error": str(exc)}


def _sse_event(event_type: str, data: dict[str, Any]) -> str:
    payload = {"type": event_type, **data}
    return f"data: {json.dumps(payload)}\n\n"
