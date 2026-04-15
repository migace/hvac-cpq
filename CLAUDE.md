# CLAUDE.md

## Project overview

This repository is a **Turborepo monorepo** containing a **data-driven CPQ PoC for HVAC products**.

The monorepo consists of:
- **backend** (`apps/backend/`) — Python, FastAPI, SQLAlchemy 2.x, PostgreSQL, Alembic,
- **frontend** (`apps/frontend/`) — React, TypeScript, Vite.

The prototype focuses on **fire dampers** as the first HVAC category, but the architecture supports many product categories, families, dynamic attributes, business rules, pricing rules, technical calculations, and quote generation.

The main goal is to model **configurable HVAC products** without hardcoding product parameters in application code.

---

## Repository structure

```
hvac-cpq/
├── apps/
│   ├── backend/            # Python FastAPI backend
│   │   ├── app/            # application code (api, core, db, domain, services, etc.)
│   │   ├── alembic/        # database migrations
│   │   ├── tests/          # backend tests
│   │   ├── scripts/        # utility scripts (seed, etc.)
│   │   └── pyproject.toml
│   └── frontend/           # React + TypeScript frontend
│       ├── src/            # React source code
│       ├── public/         # static assets
│       ├── vite.config.ts
│       └── package.json
├── docs/                   # project-wide documentation (see index below)
├── docker-compose.yml      # 3 services: db, api, frontend
├── turbo.json              # Turborepo task pipeline
├── package.json            # root workspaces config
└── CLAUDE.md               # this file
```

---

## Quick start

```bash
npm install && npm run dev          # all dev servers via Turborepo
docker compose up                   # or full Docker stack
cd apps/backend && python -m scripts.seed_demo_data  # seed demo data
```

For full setup instructions, see `docs/running.md`.

---

## Architecture summary

Backend: layered architecture (API → Service → Domain → Repository → Persistence) with cross-cutting concerns (logging, request correlation, error formatting).

Frontend: React + TypeScript SPA built with Vite. API proxy via `/api/*` in both dev (Vite) and production (nginx).

For detailed architecture, see `docs/architecture.md`.

---

## Domain model summary

Core entities: `ProductFamily`, `AttributeDefinition`, `AttributeOption`, `ProductConfiguration`, `AttributeValue`, `ProductRule`, `ProductPricingRule`, `ProductQuote`.

Key design decisions:
- EAV is used only for **configuration values**, not for every aspect of the domain,
- business rules are modeled separately in `product_rules`,
- pricing is separate from configuration storage,
- quotes store historical configuration and pricing snapshots (immutable).

For full ERD and entity descriptions, see `docs/erd.md`.

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

## Documentation index

When you need details beyond this file, consult the relevant doc:

| Topic | File | What you'll find |
|---|---|---|
| **Running & setup** | `docs/running.md` | Local dev, Docker Compose, Turborepo commands, seeding |
| **Architecture** | `docs/architecture.md` | Layered backend, frontend SPA, infrastructure, design rationale |
| **ERD & domain model** | `docs/erd.md` | All entities, relationships, Mermaid diagram |
| **Feature scope** | `docs/feature-scope.md` | Current capabilities (families, rules, pricing, agent, etc.) |
| **Services** | `docs/services.md` | Domain services, AI agent service, tool layer |
| **API conventions** | `docs/api-conventions.md` | Error shape, status codes, logging, SSE protocol |
| **Testing** | `docs/testing.md` | Test strategy, categories, agent evaluation approach |
| **Demo families** | `docs/demo-families.md` | Fire damper families used for demo/seed |
| **Data ingestion** | `docs/data-ingestion.md` | PDF/Excel ingestion pipeline philosophy |
| **Recruitment summary** | `docs/recruitment-submission.md` | Strengths, limitations, PoC context |

---

## Current status

This project is intentionally a PoC. It demonstrates data-driven product modeling, dynamic attributes, business rules, pricing, quote snapshots, AI product advisor, and full-stack Docker Compose setup with Turborepo.

For a full summary of strengths and limitations, see `docs/recruitment-submission.md`.
