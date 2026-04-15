Intelligently run tests based on what code has changed. Analyze failures and suggest fixes.

## Context

- Backend tests: `apps/backend/tests/` — pytest with PostgreSQL testcontainers
- Frontend tests: `apps/frontend/` — Vitest (if configured) or Playwright e2e in `apps/frontend/e2e/`
- Monorepo test command: `npm run test` (via Turborepo)
- Backend test command: `cd apps/backend && python -m pytest -v`
- Frontend e2e: `cd apps/frontend && npx playwright test`

### Backend test files and what they cover

| Test file | Tests for |
|---|---|
| `test_product_families.py` | Family CRUD, duplicate checks, enum validation |
| `test_product_configurations.py` | Configuration creation, attribute validation |
| `test_product_rules.py` | Business rule creation, validation |
| `test_product_quotes.py` | Quote generation |
| `test_pricing.py` | Pricing calculation engine |
| `test_order_code.py` | Order code generation |
| `test_agent_chat.py` | AI agent chat integration |
| `test_agent_tools.py` | AI agent tool execution |
| `test_error_handling.py` | Error response formatting |
| `test_health.py` | Health check endpoint |

### Test infrastructure

- `conftest.py` uses testcontainers for PostgreSQL — a real database is spun up per test session
- Fixtures: `db_session`, `client` (FastAPI TestClient), `clean_database` (truncates between tests)
- Tests use FastAPI dependency overrides to inject test DB session

## Steps

### 1. Detect what changed

Run `git diff --name-only` (unstaged) and `git diff --cached --name-only` (staged).
If no local changes, use `git diff --name-only main...HEAD` for branch changes.

### 2. Map changes to tests

Use this mapping to determine which tests to run:

| Changed file pattern | Run tests |
|---|---|
| `app/db/models.py` | ALL backend tests |
| `app/services/product_family_service.py` | `test_product_families.py` |
| `app/services/product_configuration_service.py` | `test_product_configurations.py` |
| `app/services/rule_engine.py` | `test_product_rules.py` |
| `app/services/pricing_engine.py` | `test_pricing.py` |
| `app/services/product_quote_service.py` | `test_product_quotes.py` |
| `app/services/order_code_service.py` | `test_order_code.py` |
| `app/services/agent/*` | `test_agent_chat.py`, `test_agent_tools.py` |
| `app/services/configuration_validator.py` | `test_product_configurations.py` |
| `app/repositories/*` | Tests for the corresponding domain |
| `app/schemas/*` | Tests for the corresponding domain |
| `app/api/routes/*` | Tests for the corresponding domain |
| `app/core/*` | ALL backend tests |
| `app/domain/*` | ALL backend tests |
| `tests/conftest.py` | ALL backend tests |
| `apps/frontend/src/*` | Frontend e2e tests |

### 3. Run targeted tests

Run only the relevant tests:

```bash
cd apps/backend && python -m pytest tests/test_specific_file.py -v
```

If ALL backend tests are needed:

```bash
cd apps/backend && python -m pytest -v
```

If frontend changes detected:

```bash
cd apps/frontend && npx playwright test
```

### 4. Analyze results

For each failure:
- Read the full traceback
- Identify root cause (code bug vs test bug vs environment issue)
- Read the relevant source code
- Suggest a specific fix with file path and line number

### 5. Report

Present results as:

### Test results

**Scope**: which tests were run and why
**Result**: X passed, Y failed, Z skipped

#### Failures (if any)
For each failure:
- **Test**: `test_name` in `test_file.py`
- **Error**: one-line summary
- **Root cause**: what's actually wrong
- **Fix**: specific code change needed

#### Coverage notes
- Areas of changed code NOT covered by existing tests
- Suggested new tests if gaps are found

## Important

- NEVER modify test infrastructure (conftest.py) unless specifically asked
- If tests require a running database and testcontainers fails, inform the user about Docker requirements
- If a test fails due to a missing dependency, suggest `pip install` rather than skipping
- Run tests with `-v` flag for detailed output
- If ALL tests pass, say so concisely — don't over-explain success
