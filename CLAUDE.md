# CLAUDE.md

## Project overview

This repository is a **Turborepo monorepo** containing a **data-driven CPQ PoC for HVAC products**.

The monorepo consists of:
- **backend** (`apps/backend/`) — Python, FastAPI, SQLAlchemy 2.x, PostgreSQL, Alembic,
- **frontend** (`apps/frontend/`) — React, TypeScript, Vite.

The prototype focuses on **fire dampers** as the first HVAC category, but the architecture is intentionally designed to support:
- many product categories,
- many product families,
- dynamic attributes,
- business validation rules,
- pricing rules,
- technical calculations,
- quote generation.

The main goal of the project is to model **configurable HVAC products** without hardcoding all product parameters in application code.

---

## Repository structure

```
hvac-cpq/
├── apps/
│   ├── backend/            # Python FastAPI backend
│   │   ├── app/            # application code (api, core, db, domain, services, etc.)
│   │   ├── alembic/        # database migrations
│   │   ├── tests/          # backend tests
│   │   ├── scripts/        # utility scripts
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── alembic.ini
│   │   └── .env.example
│   └── frontend/           # React + TypeScript frontend
│       ├── src/            # React source code
│       ├── public/         # static assets
│       ├── Dockerfile      # multi-stage: node build -> nginx
│       ├── nginx.conf      # SPA serving + API proxy
│       ├── vite.config.ts
│       └── package.json
├── docs/                   # project-wide documentation
├── docker-compose.yml      # 3 services: db, api, frontend
├── turbo.json              # Turborepo task pipeline
├── package.json            # root workspaces config
└── CLAUDE.md               # this file
```

---

## Running the project

### Local development

```bash
# Install Node dependencies (Turborepo + frontend)
npm install

# Run all dev servers via Turborepo
npm run dev

# Run only frontend
npx turbo run dev --filter=@hvac-cpq/frontend

# Run only backend (requires Python venv in apps/backend/)
npx turbo run dev --filter=@hvac-cpq/backend
```

Backend requires a Python virtual environment set up in `apps/backend/`:
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Docker Compose

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

### Turborepo commands

| Command | Description |
|---|---|
| `npm run dev` | Start all dev servers |
| `npm run build` | Build all apps |
| `npm run lint` | Lint all apps |
| `npm run test` | Run all tests |

---

## Business context

HVAC manufacturers typically have:
- many product families,
- multiple variants per family,
- many configuration options,
- business constraints between parameters,
- pricing logic depending on selected options,
- product knowledge distributed across PDFs, Excel files, legacy tools, and expert knowledge.

This project addresses that by building a **CPQ-oriented monorepo** where:
- a product family defines the structure of a configurable product,
- attribute definitions describe available parameters,
- configurations store concrete user selections,
- rules validate allowed combinations,
- pricing rules calculate price,
- technical calculation services compute selected technical outputs,
- quotes persist historical pricing and configuration snapshots,
- the frontend provides the user interface for product configuration.

---

## Architecture

The backend (`apps/backend/`) uses a layered architecture: API → Service → Domain → Repository → Persistence, with cross-cutting concerns (logging, request correlation, error formatting).

The frontend (`apps/frontend/`) is a React + TypeScript SPA built with Vite. In dev mode, Vite proxies `/api/*` to `http://localhost:8000`. In Docker, nginx serves the SPA and proxies `/api/` to the backend.

For detailed architecture description, see `docs/architecture.md`.

---

## Current feature scope

The current implementation supports:

### 1. Product family modeling
- create product families,
- define dynamic attributes,
- support multiple attribute types,
- define enum options,
- mark attributes as required,
- define numeric ranges and units.

### 2. EAV configuration storage
- create a product configuration,
- store selected values in EAV form,
- support `string`, `integer`, `decimal`, `boolean`, and `enum` values,
- validate attribute existence and value type.

### 3. Complete configuration validation
- reject empty configurations,
- reject missing required attributes,
- reject unknown attribute codes,
- reject invalid enum/range/type combinations.

### 4. Business rules engine
Supports rule types:
- `requires_attribute`,
- `forbids_attribute`,
- `restricts_value`.

Supports condition operators:
- `eq`,
- `neq`,
- `gt`,
- `gte`,
- `lt`,
- `lte`,
- `in`.

### 5. Pricing engine
Supports pricing rule types:
- `base_price`,
- `fixed_surcharge`,
- `percentage_surcharge`.

Returns:
- currency,
- base price,
- surcharge total,
- final price,
- price breakdown.

### 6. Quote generation
Supports:
- quote creation for an existing configuration,
- quote number generation,
- quote status,
- historical configuration snapshot,
- historical pricing snapshot.

### 7. Order code generation
Supports simple family-specific order code generation for selected fire damper families.

### 8. Technical calculations
Supports example technical calculations such as effective area for rectangular and round fire dampers.

### 9. Demo data seeding
Supports seeding of demo families such as:
- `fire_damper_rectangular`,
- `fire_damper_round`,
- `multi_blade_fire_damper`.

---

## Domain model

Core entities: `ProductFamily`, `AttributeDefinition`, `AttributeOption`, `ProductConfiguration`, `AttributeValue`, `ProductRule`, `ProductPricingRule`, `ProductQuote`.

Main tables: `product_families`, `attribute_definitions`, `attribute_options`, `product_configurations`, `attribute_values`, `product_rules`, `product_pricing_rules`, `product_quotes`.

Key design decisions:
- EAV is used only for **configuration values**, not for every aspect of the domain,
- business rules are modeled separately in `product_rules`,
- pricing is separate from configuration storage,
- quotes store historical configuration and pricing snapshots (immutable).

For full ERD and entity descriptions, see `docs/erd.md`.

---

## Important services

### `ProductFamilyService`
Creates and reads product families and their attribute definitions.

### `ProductConfigurationService`
Handles:
- configuration validation,
- value normalization,
- EAV persistence,
- price calculation preparation,
- shared configuration value mapping.

### `ConfigurationValidator`
Checks:
- empty configuration,
- required attributes presence.

### `RuleEngine`
Evaluates business rules against normalized configuration values.

### `PricingEngine`
Calculates price and returns structured breakdown.

### `ProductQuoteService`
Creates quotes and stores pricing/configuration snapshots.

### `OrderCodeService`
Builds order codes based on family and selected configuration values.

### `TechnicalCalculationService`
Computes selected technical outputs from valid configuration input.

---

## API overview

The backend exposes API endpoints for:
- health check,
- product families,
- product configurations,
- product rules,
- product pricing rules,
- product quotes,
- price calculation,
- order code generation,
- technical parameter calculation.

The routing structure should stay clear and resource-oriented.

The frontend communicates with the backend via `/api/*` proxy (both in dev and production).

---

## Error handling conventions

The API uses a consistent error shape:
- `type`
- `message`
- `code`
- `request_id`
- optional `details`

Error classes are separated into:
- request validation errors,
- domain errors,
- database errors,
- unexpected internal errors.

### Status code conventions
- `400` for domain-level invalid requests,
- `404` for missing resources,
- `409` for conflicts and integrity violations,
- `422` for request payload validation errors,
- `500` for unexpected internal/system errors.

---

## Logging and request context

The application uses:
- structured logging,
- per-request correlation via `request_id`,
- request/response logging middleware,
- consistent error logging.

The request id should be preserved in:
- logs,
- error responses,
- response headers.

---

## Testing strategy

### Backend tests
Located in `apps/backend/tests/`.

The test setup is designed to keep application development data separate from test data.

#### Current testing principles
- test DB must be isolated from dev DB,
- API tests should use dependency overrides,
- tests should validate both happy path and failure path,
- rules, pricing, order code generation, and technical calculations should be covered.

#### Recommended direction
Use a dedicated PostgreSQL test container instead of SQLite when validating production-like behavior.

### Frontend tests
Frontend testing infrastructure can be extended with Vitest.

---

## Seeding strategy

Demo seed data should illustrate that the model supports multiple families inside one category.

Current recommended demo families:
- `fire_damper_rectangular`
- `fire_damper_round`
- `multi_blade_fire_damper`

The seed should include:
- attribute definitions,
- enum options,
- business rules,
- pricing rules.

### Running the seed

```bash
cd apps/backend
python -m scripts.seed_demo_data
```

The script is located at `apps/backend/scripts/seed_demo_data.py`. It skips families that already exist in the database.

---

## Product data ingestion approach

PDF and Excel should be treated as **source materials**, not as the long-term source of truth. The structured CPQ data model in PostgreSQL is the operational source of truth.

For the full ingestion pipeline description, see `docs/data-ingestion.md`.

---

## Order code generation philosophy

Order codes are generated only for **valid** configurations.
That means:
- configuration must pass payload validation,
- required attributes must be present,
- rules engine must pass,
- family must have a defined order code strategy.

The current PoC uses:
- family prefix mapping,
- segment composition based on selected attributes,
- simple value-to-code mappings.

This can later evolve into a data-driven order code templating system.

---

## Technical calculation philosophy

Technical calculations are intentionally separated from:
- rules,
- pricing,
- persistence.

The current PoC includes example calculations such as:
- effective area for rectangular fire dampers,
- effective area for round fire dampers.

This service is intended to evolve into a more advanced formula/calculation engine in the future.

---

## Docker and infrastructure

Docker Compose (`docker-compose.yml`) runs 3 services: `db` (PostgreSQL 16, port 5432), `api` (FastAPI, port 8000), `frontend` (nginx, port 3000).

Backend environment: `apps/backend/.env` for local dev, `docker-compose.yml` env block for Docker. See `apps/backend/.env.example` for the full list.

For detailed infrastructure description, see `docs/architecture.md`.

---

## Current status

This project is intentionally a PoC. It demonstrates data-driven product modeling, dynamic attributes, business rules, pricing, quote snapshots, and full-stack Docker Compose setup with Turborepo.

For a full summary of strengths and limitations, see `docs/recruitment-submission.md`.

---

## Development guidelines

### General principles
- do not hardcode individual product parameters into route handlers,
- keep the domain data-driven,
- keep pricing separate from validation,
- keep rules separate from storage,
- keep quote snapshots immutable,
- prefer explicit business logic over hidden ORM magic,
- prefer clear code over premature abstraction.

### Monorepo conventions
- backend code lives in `apps/backend/`,
- frontend code lives in `apps/frontend/`,
- project-wide documentation lives in `docs/`,
- root `package.json` defines workspaces and Turborepo scripts,
- each app has its own `Dockerfile` and can be built independently.

### When adding new HVAC families
For every new family, think in this order:
1. what is the family code and purpose,
2. what are the required and optional attributes,
3. which attributes are enums and what are their options,
4. which rules define valid combinations,
5. which pricing rules apply,
6. how order code should be built,
7. which technical calculations are needed.

### When adding new business rules
- validate referenced attributes exist in the family,
- prefer deterministic rule behavior,
- keep error messages business-readable,
- add tests for valid and invalid configurations.

### When adding new pricing rules
- keep exactly one active base price rule per family,
- separate fixed and percentage logic clearly,
- always return structured pricing breakdown.

### When adding new technical calculations
- run them only on validated configuration values,
- keep unit handling explicit,
- prefer deterministic outputs,
- add API tests for expected formulas.

---

## Suggested repository hygiene

Keep `CLAUDE.md` concise enough to be useful as a high-signal project guide.

Detailed materials belong in `docs/`.

Current documentation files:
- `docs/architecture.md`
- `docs/erd.md`
- `docs/data-ingestion.md`
- `docs/demo-families.md`
- `docs/recruitment-submission.md`

---

## Recommended next steps

The most valuable next improvements are:
1. build frontend UI for product configuration workflow,
2. integrate technical calculation results into quote snapshots,
3. improve demo flow documentation,
4. expand observability and deployment readiness,
5. prepare a polished recruitment-oriented README/submission summary.
