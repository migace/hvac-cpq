# Recruitment submission summary

## Problem

HVAC manufacturers typically manage product knowledge across:
- PDF catalogs,
- Excel sheets,
- legacy tools,
- internal engineering knowledge.

Even within one category such as fire dampers, there are:
- multiple product families,
- many configuration parameters,
- family-specific validation rules,
- family-specific pricing logic,
- technical calculations,
- business outputs like order codes and offers.

The main challenge is to design a product model that supports all of that without hardcoding parameters in the application.

---

## What was built

This PoC implements a **data-driven CPQ system** for HVAC products, structured as a **Turborepo monorepo**.

### Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy 2.x, Alembic |
| Database | PostgreSQL 16 |
| Frontend | React, TypeScript, Vite |
| Monorepo | Turborepo, npm workspaces |
| Infrastructure | Docker Compose (3 services) |

The first modeled category is **fire dampers**.

---

## What the PoC currently supports

### Product model
- product families,
- dynamic attribute definitions,
- enum options,
- required/optional fields,
- numeric ranges and units.

### Configuration engine
- EAV-based configuration storage,
- validation of value types,
- validation of required fields,
- family-specific configuration structure.

### Rules engine
- family-specific business rules,
- conditional validation between attributes,
- support for rule types like required/forbidden/restricted value.

### Pricing engine
- base price,
- fixed surcharge,
- percentage surcharge,
- structured price breakdown.

### Quote generation
- quote creation for a valid configuration,
- quote number,
- historical configuration snapshot,
- historical pricing snapshot.

### Business outputs
- order code generation,
- example technical parameter calculation,
- demo seed for 3 fire damper families.

### Full-stack infrastructure
- Turborepo monorepo with backend and frontend apps,
- Docker Compose with PostgreSQL, backend API, and frontend,
- API proxy in both development (Vite) and production (nginx) modes.

---

## Repository structure

```
hvac-cpq/
├── apps/
│   ├── backend/     # Python FastAPI — CPQ API, business logic, persistence
│   └── frontend/    # React + TypeScript — user interface
├── docs/            # project-wide documentation
├── docker-compose.yml
├── turbo.json
└── package.json
```

---

## Architecture summary

The system is structured into:
- **backend** — API layer, service layer, domain layer, repository layer, persistence layer,
- **frontend** — React SPA with Vite, API proxy to backend,
- **infrastructure** — Docker Compose with 3 services (db, api, frontend).

This separation keeps:
- data model flexible,
- validation explicit,
- pricing explicit,
- quote generation stable,
- frontend and backend independently buildable,
- future extension easier.

---

## Why this approach

The most important design decision was to treat product definition as **data**, not code.

That is why:
- families are dynamic,
- attributes are dynamic,
- configuration values use EAV,
- rules are stored separately,
- pricing is stored separately,
- quotes store snapshots.

The monorepo with Turborepo was chosen to:
- keep backend and frontend in one repository,
- share a single Docker Compose for full-stack development,
- enable unified task execution (dev, build, lint, test).

This makes the model much more suitable for a real HVAC manufacturer environment.

---

## How product data would be onboarded

Source materials such as PDF and Excel are treated as:
- source inputs,
- not as long-term source of truth.

Recommended ingestion flow:
1. source inventory,
2. extraction of family/attribute knowledge,
3. normalization,
4. staging,
5. validation,
6. import into structured CPQ tables.

For the PoC, the most realistic approach is semi-manual ingestion supported by scripts/seeds.

---

## What this PoC demonstrates well

- domain modeling for configurable HVAC products,
- separation of product definition and product configuration,
- data-driven architecture,
- support for multiple product families,
- family-specific rule logic,
- family-specific pricing logic,
- historical quote persistence,
- monorepo structure ready for full-stack development,
- Docker Compose for one-command startup.

---

## Current limitations

This is intentionally still a PoC.

Not yet fully implemented:
- frontend UI for product configuration workflow,
- richer technical formula engine,
- data-driven order code templates,
- full ingestion pipeline with staging tables,
- more advanced grouped rule logic,
- full deployment hardening,
- richer observability and operations.

---

## Conclusion

The PoC is not a finished commercial product, but it demonstrates:
- how I approach the problem,
- how I model complex configurable products,
- how I structure a scalable full-stack foundation,
- how I separate domain data, rules, pricing, and business outputs,
- how I organize a monorepo for a real-world project.

The solution is intentionally built as a strong architectural core that can be extended toward a full HVAC product selection platform.
