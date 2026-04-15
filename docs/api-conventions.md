# API conventions

## Endpoint structure

The backend exposes resource-oriented API endpoints for:
- health check,
- product families,
- product configurations,
- product rules,
- product pricing rules,
- product quotes,
- price calculation,
- order code generation,
- technical parameter calculation,
- AI agent chat.

The routing structure should stay clear and resource-oriented.

The frontend communicates with the backend via `/api/*` proxy (both in dev and production).

---

## Error handling

### Error shape

The API uses a consistent error shape:
- `type`
- `message`
- `code`
- `request_id`
- optional `details`

### Error classes

Error classes are separated into:
- request validation errors,
- domain errors,
- database errors,
- unexpected internal errors.

### Status code conventions

| Code | Usage |
|---|---|
| `400` | domain-level invalid requests |
| `404` | missing resources |
| `409` | conflicts and integrity violations |
| `422` | request payload validation errors |
| `500` | unexpected internal/system errors |
| `503` | service unavailable (e.g. missing API key for agent) |

---

## Logging and request context

The application uses:
- structured logging via `structlog`,
- per-request correlation via `request_id`,
- request/response logging middleware,
- consistent error logging.

The request id should be preserved in:
- logs,
- error responses,
- response headers.

---

## Agent SSE protocol

The `POST /agent/chat` endpoint returns `text/event-stream` with the following event types:

| Event type | Payload | Description |
|---|---|---|
| `delta` | `{ content: string }` | Streamed text chunk |
| `tool_call` | `{ name: string, arguments: object }` | Agent called a tool |
| `tool_result` | `{ name: string, result: object }` | Tool returned a result |
| `done` | `{ metrics: AgentMetrics }` | Invocation complete |
| `error` | `{ message: string }` | Error occurred |
