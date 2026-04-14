import { useState, useRef, useCallback } from "react";
import type {
  ChatMessage,
  AgentSSEEvent,
  SuggestedConfiguration,
  AgentMetrics,
} from "../types";

const API_BASE = "/api";

interface UseChatOptions {
  onSuggestedConfiguration?: (config: SuggestedConfiguration) => void;
}

interface ChatState {
  messages: ChatMessage[];
  isStreaming: boolean;
  error: string | null;
  activeTools: string[];
  lastMetrics: AgentMetrics | null;
}

export function useChat(options: UseChatOptions = {}) {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isStreaming: false,
    error: null,
    activeTools: [],
    lastMetrics: null,
  });

  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (userMessage: string) => {
      if (!userMessage.trim() || state.isStreaming) return;

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      const newUserMsg: ChatMessage = { role: "user", content: userMessage };

      setState((s) => ({
        ...s,
        messages: [...s.messages, newUserMsg],
        isStreaming: true,
        error: null,
        activeTools: [],
        lastMetrics: null,
      }));

      const history = [...state.messages];
      let assistantContent = "";

      try {
        const response = await fetch(`${API_BASE}/agent/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: userMessage,
            history,
          }),
          signal: controller.signal,
        });

        if (!response.ok) {
          const err = await response.json().catch(() => ({
            message: response.statusText,
          }));
          throw new Error(err.message || "Agent request failed");
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("No response body");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;

            const eventData = line.slice(6);
            let event: AgentSSEEvent;
            try {
              event = JSON.parse(eventData);
            } catch {
              continue;
            }

            switch (event.type) {
              case "delta":
                assistantContent += event.content;
                setState((s) => {
                  const msgs = [...s.messages];
                  const lastMsg = msgs[msgs.length - 1];
                  if (lastMsg?.role === "assistant") {
                    msgs[msgs.length - 1] = {
                      ...lastMsg,
                      content: assistantContent,
                    };
                  } else {
                    msgs.push({ role: "assistant", content: assistantContent });
                  }
                  return { ...s, messages: msgs };
                });
                break;

              case "tool_call":
                setState((s) => ({
                  ...s,
                  activeTools: [...s.activeTools, event.name],
                }));
                break;

              case "tool_result":
                setState((s) => ({
                  ...s,
                  activeTools: s.activeTools.filter((t) => t !== event.name),
                }));
                break;

              case "done":
                setState((s) => ({
                  ...s,
                  lastMetrics: event.metrics,
                }));
                break;

              case "error":
                setState((s) => ({
                  ...s,
                  error: event.message,
                }));
                break;
            }
          }
        }

        // Parse suggested configuration from the final content
        const configMatch = assistantContent.match(
          /```json:suggested_configuration\s*\n([\s\S]*?)```/
        );
        if (configMatch) {
          try {
            const config: SuggestedConfiguration = JSON.parse(configMatch[1]);
            options.onSuggestedConfiguration?.(config);
          } catch {
            // malformed JSON — ignore
          }
        }
      } catch (err) {
        if ((err as Error).name === "AbortError") return;
        setState((s) => ({
          ...s,
          error: (err as Error).message || "Failed to connect to agent",
        }));
      } finally {
        setState((s) => ({ ...s, isStreaming: false, activeTools: [] }));
      }
    },
    [state.messages, state.isStreaming, options]
  );

  const clearHistory = useCallback(() => {
    abortRef.current?.abort();
    setState({
      messages: [],
      isStreaming: false,
      error: null,
      activeTools: [],
      lastMetrics: null,
    });
  }, []);

  return {
    messages: state.messages,
    isStreaming: state.isStreaming,
    error: state.error,
    activeTools: state.activeTools,
    lastMetrics: state.lastMetrics,
    sendMessage,
    clearHistory,
  };
}
