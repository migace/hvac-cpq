# Testing strategy

## Backend tests

Located in `apps/backend/tests/`.

The test setup is designed to keep application development data separate from test data.

### Testing principles
- test DB must be isolated from dev DB,
- API tests should use dependency overrides,
- tests should validate both happy path and failure path,
- rules, pricing, order code generation, and technical calculations should be covered.

### Test infrastructure
- PostgreSQL test container via `testcontainers` for production-like isolation,
- `conftest.py` provides `TestClient` with dependency injection override,
- database cleanup between tests,
- session factory for isolated DB access.

### Test categories

| Category | File | What it covers |
|---|---|---|
| Product families | `test_product_families.py` | CRUD, attribute definitions |
| Configurations | `test_product_configurations.py` | EAV storage, validation |
| Rules | `test_product_rules.py` | Business rule creation and enforcement |
| Pricing | `test_product_pricing_rules.py` | Pricing rule creation and calculation |
| Quotes | `test_product_quotes.py` | Quote creation, snapshots |
| Agent API | `test_agent_api.py` | Endpoint validation, SSE format, error handling |
| Agent tools | `test_agent_tools.py` | Each tool in isolation with real DB |
| Agent evaluation | `test_agent_evaluation.py` | Golden test cases, workflow simulation |

### Agent testing approach

The agent is tested in three layers:

1. **API contract tests** (`test_agent_api.py`) — validate endpoint behavior without calling OpenAI (mocked). Covers request validation, error handling, SSE format.

2. **Tool layer tests** (`test_agent_tools.py`) — each tool tested in isolation with real PostgreSQL. Verifies that tools correctly wrap domain services and return structured data.

3. **Golden evaluation cases** (`test_agent_evaluation.py`) — simulate full agent workflows step by step without LLM. Verify that the correct sequence of tool calls produces expected results. Includes a documented LLM-as-Judge framework for optional end-to-end evaluation.

### Running tests

```bash
cd apps/backend
source .venv/bin/activate
pytest
```

---

## Frontend tests

Frontend testing infrastructure can be extended with Vitest.
