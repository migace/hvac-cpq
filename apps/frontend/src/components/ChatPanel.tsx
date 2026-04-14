import { useState, useRef, useEffect, useCallback } from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Fab from "@mui/material/Fab";
import Chip from "@mui/material/Chip";
import Tooltip from "@mui/material/Tooltip";
import Fade from "@mui/material/Fade";
import CircularProgress from "@mui/material/CircularProgress";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import SendIcon from "@mui/icons-material/Send";
import CloseIcon from "@mui/icons-material/Close";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import BuildIcon from "@mui/icons-material/Build";
import { useChat } from "../hooks/useChat";
import type { SuggestedConfiguration } from "../types";

interface ChatPanelProps {
  onSuggestedConfiguration?: (config: SuggestedConfiguration) => void;
}

const TOOL_LABELS: Record<string, string> = {
  search_products: "Searching products",
  get_family_details: "Loading details",
  calculate_price: "Calculating price",
  validate_configuration: "Validating",
  generate_order_code: "Generating code",
  calculate_technical_params: "Computing specs",
};

export default function ChatPanel({
  onSuggestedConfiguration,
}: ChatPanelProps) {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { messages, isStreaming, error, activeTools, lastMetrics, sendMessage, clearHistory } =
    useChat({
      onSuggestedConfiguration,
    });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, activeTools]);

  const handleSubmit = useCallback(
    (e?: React.FormEvent) => {
      e?.preventDefault();
      if (!input.trim() || isStreaming) return;
      sendMessage(input);
      setInput("");
    },
    [input, isStreaming, sendMessage]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const renderContent = (content: string) => {
    // Strip the suggested_configuration JSON block from display
    const cleaned = content.replace(
      /```json:suggested_configuration\s*\n[\s\S]*?```/g,
      ""
    );
    // Simple markdown-like rendering for bold/code/newlines
    return cleaned.split("\n").map((line, i) => {
      if (!line.trim()) return <br key={i} />;

      const parts = line.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((part, j) => {
        if (part.startsWith("`") && part.endsWith("`")) {
          return (
            <Box
              key={j}
              component="span"
              sx={{
                fontFamily: "monospace",
                bgcolor: "action.hover",
                px: 0.5,
                borderRadius: 0.5,
                fontSize: "0.85em",
              }}
            >
              {part.slice(1, -1)}
            </Box>
          );
        }
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={j}>{part.slice(2, -2)}</strong>
          );
        }
        return part;
      });

      return (
        <Typography
          key={i}
          variant="body2"
          component="div"
          sx={{ lineHeight: 1.6 }}
        >
          {parts}
        </Typography>
      );
    });
  };

  return (
    <>
      {/* Floating action button */}
      <Fade in={!open}>
        <Fab
          color="primary"
          onClick={() => setOpen(true)}
          sx={{
            position: "fixed",
            bottom: 24,
            right: 24,
            zIndex: 1300,
          }}
        >
          <SmartToyIcon />
        </Fab>
      </Fade>

      {/* Chat panel */}
      <Fade in={open}>
        <Paper
          elevation={8}
          sx={{
            position: "fixed",
            bottom: 24,
            right: 24,
            width: { xs: "calc(100vw - 48px)", sm: 420 },
            height: { xs: "calc(100vh - 96px)", sm: 560 },
            zIndex: 1300,
            display: open ? "flex" : "none",
            flexDirection: "column",
            borderRadius: 3,
            overflow: "hidden",
          }}
        >
          {/* Header */}
          <Box
            sx={{
              px: 2,
              py: 1.5,
              bgcolor: "primary.main",
              color: "primary.contrastText",
              display: "flex",
              alignItems: "center",
              gap: 1,
            }}
          >
            <SmartToyIcon fontSize="small" />
            <Typography variant="subtitle1" sx={{ flex: 1, fontWeight: 600 }}>
              AI Product Advisor
            </Typography>
            <Tooltip title="Clear history">
              <IconButton
                size="small"
                sx={{ color: "inherit" }}
                onClick={clearHistory}
              >
                <DeleteOutlinedIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <IconButton
              size="small"
              sx={{ color: "inherit" }}
              onClick={() => setOpen(false)}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>

          {/* Messages area */}
          <Box
            sx={{
              flex: 1,
              overflowY: "auto",
              px: 2,
              py: 1.5,
              display: "flex",
              flexDirection: "column",
              gap: 1.5,
              bgcolor: "grey.50",
            }}
          >
            {messages.length === 0 && (
              <Box sx={{ textAlign: "center", mt: 4 }}>
                <SmartToyIcon
                  sx={{ fontSize: 48, color: "grey.300", mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Ask me about HVAC products!
                </Typography>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  component="div"
                  sx={{ mt: 1 }}
                >
                  Try: "I need an EI120 rectangular fire damper 400x300"
                </Typography>
              </Box>
            )}

            {messages.map((msg, i) => (
              <Box
                key={i}
                sx={{
                  display: "flex",
                  justifyContent:
                    msg.role === "user" ? "flex-end" : "flex-start",
                }}
              >
                <Box
                  sx={{
                    maxWidth: "85%",
                    px: 1.5,
                    py: 1,
                    borderRadius: 2,
                    bgcolor:
                      msg.role === "user" ? "primary.main" : "background.paper",
                    color:
                      msg.role === "user"
                        ? "primary.contrastText"
                        : "text.primary",
                    boxShadow: msg.role === "assistant" ? 1 : 0,
                  }}
                >
                  {msg.role === "user" ? (
                    <Typography variant="body2">{msg.content}</Typography>
                  ) : (
                    renderContent(msg.content)
                  )}
                </Box>
              </Box>
            ))}

            {/* Active tool calls indicator */}
            {activeTools.length > 0 && (
              <Box
                sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}
              >
                {activeTools.map((tool) => (
                  <Chip
                    key={tool}
                    icon={<BuildIcon />}
                    label={TOOL_LABELS[tool] || tool}
                    size="small"
                    variant="outlined"
                    color="primary"
                    sx={{ animation: "pulse 1.5s infinite" }}
                  />
                ))}
              </Box>
            )}

            {isStreaming && activeTools.length === 0 && messages[messages.length - 1]?.role !== "assistant" && (
              <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
                <CircularProgress size={16} />
                <Typography variant="caption" color="text.secondary">
                  Thinking...
                </Typography>
              </Box>
            )}

            {error && (
              <Typography variant="body2" color="error" sx={{ px: 1 }}>
                {error}
              </Typography>
            )}

            {/* Metrics display (subtle) */}
            {lastMetrics && !isStreaming && (
              <Typography
                variant="caption"
                color="text.disabled"
                sx={{ textAlign: "center", mt: 0.5 }}
              >
                {lastMetrics.total_tokens} tokens
                {" · "}
                {(lastMetrics.total_duration_ms / 1000).toFixed(1)}s
                {lastMetrics.tool_calls_count > 0 && (
                  <>
                    {" · "}
                    {lastMetrics.tool_calls_count} tool call
                    {lastMetrics.tool_calls_count !== 1 ? "s" : ""}
                  </>
                )}
              </Typography>
            )}

            <div ref={messagesEndRef} />
          </Box>

          {/* Input area */}
          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{
              p: 1.5,
              borderTop: 1,
              borderColor: "divider",
              display: "flex",
              gap: 1,
              bgcolor: "background.paper",
            }}
          >
            <TextField
              fullWidth
              size="small"
              placeholder="Describe what you need..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isStreaming}
              multiline
              maxRows={3}
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 2,
                },
              }}
            />
            <IconButton
              type="submit"
              color="primary"
              disabled={!input.trim() || isStreaming}
              sx={{ alignSelf: "flex-end" }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Fade>

      {/* Pulse animation for tool chips */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </>
  );
}
