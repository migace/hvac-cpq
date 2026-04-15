Check the health of the entire HVAC CPQ development stack and report status.

## Checks to perform

Run all checks in parallel where possible, then present a unified status report.

### 1. Docker containers

```bash
docker compose ps
```

Expected services:
- `db` (postgres:16) — port 5432
- `api` (backend) — port 8000
- `frontend` — port 3000

Check if containers are running, healthy, or stopped.

### 2. Database connectivity

```bash
docker compose exec db pg_isready -U cpq -d cpq_hvac
```

Or if running locally without Docker, check if PostgreSQL is reachable on the configured port.

### 3. Backend API health

```bash
curl -s http://localhost:8000/health
```

Expected response: JSON with health status. If running via Docker, also try:

```bash
curl -s http://localhost:3012/api/health
```

(port 3012 if frontend nginx proxies `/api/*`)

### 4. Frontend dev server

Check if the frontend is accessible:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/
```

Or via Docker:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3012/
```

### 5. Alembic migration status

```bash
cd apps/backend && python -m alembic current
cd apps/backend && python -m alembic check
```

Check if the database schema is up to date with the latest migration.

### 6. Seed data presence

```bash
curl -s http://localhost:8000/product-families
```

Check if demo product families exist (fire_damper_rectangular, fire_damper_round, multi_blade_fire_damper).

### 7. Dependencies

Check if dependencies are installed:

```bash
# Root npm packages
ls node_modules/.package-lock.json 2>/dev/null && echo "npm: installed" || echo "npm: NOT installed"

# Backend Python packages
cd apps/backend && python -c "import fastapi, sqlalchemy, alembic; print('python deps: installed')" 2>/dev/null || echo "python deps: NOT installed"

# Frontend node_modules
ls apps/frontend/node_modules/.package-lock.json 2>/dev/null && echo "frontend npm: installed" || echo "frontend npm: NOT installed"
```

### 8. Environment files

Check if required `.env` files exist (without revealing their contents):

```bash
ls -la apps/backend/.env 2>/dev/null && echo ".env: exists" || echo ".env: MISSING"
```

## Output format

Present results as a status dashboard:

```
## Stack Health Report

| Component        | Status | Details                          |
|------------------|--------|----------------------------------|
| Docker           | ...    | ...                              |
| PostgreSQL       | ...    | ...                              |
| Backend API      | ...    | ...                              |
| Frontend         | ...    | ...                              |
| Migrations       | ...    | ...                              |
| Seed data        | ...    | ...                              |
| Dependencies     | ...    | ...                              |
| Environment      | ...    | ...                              |
```

Use these status indicators:
- **OK** — working as expected
- **WARN** — partially working or degraded
- **FAIL** — not working
- **SKIP** — could not check (explain why)

### Recommendations

If any component is WARN or FAIL, provide the specific command to fix it:
- Missing deps → `npm install` or `pip install -e ".[dev]"`
- DB not running → `docker compose up db -d`
- Migrations behind → `cd apps/backend && python -m alembic upgrade head`
- No seed data → `cd apps/backend && python -m scripts.seed_demo_data`
- Missing .env → list required variables from `apps/backend/app/core/config.py`
