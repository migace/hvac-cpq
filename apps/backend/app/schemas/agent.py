from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(
        description="Message role: 'user' or 'assistant'.",
        pattern="^(user|assistant)$",
    )
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="The user's message to the AI agent.",
    )
    conversation_id: str | None = Field(
        default=None,
        description="Optional conversation ID for tracking. Generated server-side if omitted.",
    )
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=50,
        description="Previous messages in the conversation for context.",
    )
