# Running the project

## Local development

### Prerequisites

```bash
# Install Node dependencies (Turborepo + frontend)
npm install
```

Backend requires a Python virtual environment set up in `apps/backend/`:
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Dev servers

```bash
# Run all dev servers via Turborepo
npm run dev

# Run only frontend
npx turbo run dev --filter=@hvac-cpq/frontend

# Run only backend (requires Python venv in apps/backend/)
npx turbo run dev --filter=@hvac-cpq/backend
```

---

## Docker Compose

```bash
# Start all 3 services: PostgreSQL, backend API, frontend
docker compose up

# Start only backend + database
docker compose up db api
```

Services:
- `db` — PostgreSQL 16 on port `5432`,
- `api` — FastAPI backend on port `8000`,
- `frontend` — React app (nginx) on port `3000`.

Backend environment: `apps/backend/.env` for local dev, `docker-compose.yml` env block for Docker. See `apps/backend/.env.example` for the full list.

---

## Turborepo commands

| Command | Description |
|---|---|
| `npm run dev` | Start all dev servers |
| `npm run build` | Build all apps |
| `npm run lint` | Lint all apps |
| `npm run test` | Run all tests |

---

## Seeding demo data

Demo seed data illustrates that the model supports multiple families inside one category.

Current demo families:
- `fire_damper_rectangular`
- `fire_damper_round`
- `multi_blade_fire_damper`

The seed includes attribute definitions, enum options, business rules, and pricing rules.

```bash
cd apps/backend
python -m scripts.seed_demo_data
```

The script is located at `apps/backend/scripts/seed_demo_data.py`. It skips families that already exist in the database.

For details on demo families, see `docs/demo-families.md`.
