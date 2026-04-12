# HVAC CPQ PoC

A **data-driven CPQ backend PoC for HVAC manufacturers** built in **Python** with **FastAPI**, **SQLAlchemy 2.x**, **PostgreSQL**, and **Alembic**.

This project was created as as weekend-project focused on designing a **product selection/configuration system** for HVAC manufacturers with complex, configurable product portfolios.

The prototype focuses on **fire dampers** as the first category, but the architecture is intentionally designed to support:

* multiple HVAC categories,
* multiple product families,
* dynamic attributes,
* business validation rules,
* pricing rules,
* technical calculations,
* order code generation,
* quote generation.

---

## Problem statement

HVAC manufacturers usually manage product knowledge across:

* PDF product cards,
* Excel sheets,
* legacy HTML tools,
* engineering know-how,
* ad hoc internal configuration logic.

Even within a single category such as **fire dampers**, there are:

* many product families,
* different shapes and dimensional systems,
* multiple fire classes,
* optional actuators and accessories,
* family-specific validation rules,
* family-specific pricing logic,
* business outputs like order codes and quotes.

The key challenge is to design a backend that does **not hardcode product parameters in code**, but instead models product definition as **data**.

---

## Goal of this PoC

The goal of the PoC is **not** to build a full commercial product.

The goal is to demonstrate:

* architectural thinking,
* a scalable data model,
* an approach to configurable HVAC products,
* a clear workflow for turning product knowledge into a structured CPQ system.

---

## What is implemented

### 1. Product family modeling

The system supports product families such as:

* `fire_damper_rectangular`
* `fire_damper_round`
* `multi_blade_fire_damper`

Each family can define:

* dynamic attributes,
* enum options,
* required and optional fields,
* numeric ranges,
* units.

### 2. EAV configuration model

Concrete product configurations are stored using an **EAV-based approach**:

* family definition is separate from configuration values,
* new attributes do not require schema changes,
* families may have different sets of parameters.

### 3. Configuration validation

The system validates:

* request payload shape,
* required attributes,
* numeric ranges,
* enum values,
* presence of attributes in the selected family.

### 4. Business rules engine

The PoC supports family-specific business rules such as:

* `requires_attribute`
* `forbids_attribute`
* `restricts_value`

Example:

* if `fire_class = EI120`, `actuator_type` is required.

### 5. Pricing engine

The PoC supports pricing rules such as:

* `base_price`
* `fixed_surcharge`
* `percentage_surcharge`

The result includes:

* base price,
* surcharge total,
* total price,
* structured price breakdown.

### 6. Quote generation

The system can generate a quote for a valid configuration.
A quote stores:

* final calculated price,
* configuration snapshot,
* pricing snapshot,
* quote number,
* quote status.

This means historical quotes remain stable even if business rules or prices change later.

### 7. Order code generation

The PoC includes a simple order code generator for selected fire damper families.

Example output:

* `FDR-EI120-1200x800-REIN-WALL`
* `FDO-EI60-D500-STD-CEIL`

### 8. Technical calculations

The PoC includes example technical calculations such as:

* effective area for rectangular fire dampers,
* effective area for round fire dampers.

### 9. Demo data seed

The project includes demo seed data for multiple fire damper families, proving that the architecture is not hardcoded to a single product structure.

---

## Architecture

The project uses a layered architecture.

### API layer

Responsible for:

* FastAPI routes,
* request/response schemas,
* dependency injection,
* HTTP error mapping.

### Service layer

Responsible for:

* use case orchestration,
* validation,
* rule execution,
* pricing calculation,
* quote generation,
* order code generation,
* technical calculations.

### Domain layer

Responsible for:

* business meaning,
* domain exceptions,
* product configuration semantics.

### Repository layer

Responsible for:

* query encapsulation,
* correct loading of related entities,
* reducing repeated ORM query logic.

### Persistence layer

Responsible for:

* SQLAlchemy ORM models,
* PostgreSQL schema,
* Alembic migrations,
* DB sessions.

### Cross-cutting concerns

Responsible for:

* structured logging,
* request correlation,
* consistent API error responses,
* observability integration points.

More details are available in [`docs/architecture.md`](docs/architecture.md).

---

## Data model

Main tables:

* `product_families`
* `attribute_definitions`
* `attribute_options`
* `product_configurations`
* `attribute_values`
* `product_rules`
* `product_pricing_rules`
* `product_quotes`

### Key design decisions

* **EAV is used for configuration values**, not for the entire system.
* **Business rules are modeled separately** from EAV.
* **Pricing rules are modeled separately** from validation rules.
* **Quotes store snapshots** to preserve historical business correctness.

ERD and relationship details are available in [`docs/erd.md`](docs/erd.md).

![mermaid-db-diagram.png](docs/mermaid-db-diagram.png)

---

## Product data ingestion approach

This PoC assumes that HVAC product knowledge usually comes from:

* PDF catalogs,
* Excel sheets,
* legacy HTML tools,
* engineering know-how.

Recommended ingestion flow:

1. collect source materials,
2. extract family and attribute knowledge,
3. normalize naming and units,
4. map to staging structures,
5. validate quality,
6. import into CPQ tables.

For the PoC, the preferred approach is **semi-manual ingestion** supported by scripts and normalized data structures.

More details are available in [`docs/data-ingestion.md`](docs/data-ingestion.md).

---

## Demo product families

The current demo setup includes:

* `fire_damper_rectangular`
* `fire_damper_round`
* `multi_blade_fire_damper`

These families demonstrate:

* different attribute sets,
* different rule sets,
* different pricing logic,
* rectangular and round dimension logic,
* extensibility of the model.

More details are available in [`docs/demo-families.md`](docs/demo-families.md).

---

## Repository structure

```text
app/
  api/
  core/
  db/
  domain/
  observability/
  repositories/
  schemas/
  services/
  main.py
alembic/
docs/
scripts/
tests/
CLAUDE.md
README.md
```

---

## Local development setup

### Requirements

* Python 3.12+
* PostgreSQL
* Docker (recommended)

### Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Environment

Create `.env` based on `.env.example`.

Example:

```env
APP_NAME=cpq-hvac
APP_ENV=local
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000

DATABASE_URL=postgresql+psycopg://cpq:cpq@localhost:5432/cpq_hvac

LOG_LEVEL=INFO
OTEL_ENABLED=false
```

### Run database migrations

```bash
alembic upgrade head
```

### Run the application

```bash
uvicorn app.main:app --reload
```

### Open API docs

```text
http://localhost:8000/docs
```

---

## Docker setup

Run the application and PostgreSQL with Docker Compose:

```bash
docker compose up --build
```

Then run migrations inside the app container if needed.

---

## Demo seed

After migrations, seed demo families:

```bash
python scripts/seed_demo_data.py
```

This will create demo product families, attributes, rules, and pricing rules for the fire damper category.

---

## Example flows

### 1. Create configuration

Use `POST /product-configurations` with valid family attribute values.

### 2. Calculate price

Use `POST /product-configurations/calculate-price`.

### 3. Generate order code

Use `POST /product-configurations/generate-order-code`.

### 4. Calculate technical parameters

Use `POST /product-configurations/calculate-technical`.

### 5. Generate quote

Use `POST /product-quotes` for an existing saved configuration.

---

## Testing

Run tests with:

```bash
pytest
```

### Test strategy

The test suite is intended to validate:

* happy paths,
* invalid configurations,
* rule violations,
* pricing behavior,
* order code generation,
* technical calculations,
* quote generation.

A PostgreSQL-backed test environment is recommended for production-like behavior.

---

## Error handling

The API returns a consistent error shape:

* `type`
* `message`
* `code`
* `request_id`
* optional `details`

The system distinguishes between:

* request validation errors,
* domain errors,
* database errors,
* unexpected internal errors.

This improves API consistency, debugging, and observability.

---

## Why this design

The most important design choice was to treat product definition as **data**, not code.

That is why:

* families are dynamic,
* attributes are dynamic,
* configurations use EAV,
* rules are stored separately,
* pricing is stored separately,
* quotes store immutable business snapshots.

This makes the project much closer to a real HVAC CPQ foundation than a hardcoded product form.

---

## Current strengths

This PoC already demonstrates:

* scalable product family modeling,
* flexible configuration via EAV,
* explicit validation rules,
* explicit pricing rules,
* quote persistence with snapshots,
* order code generation,
* technical calculations,
* multi-family demo support.

These are the strongest parts of the current implementation.

---

## Current limitations

This is intentionally still a PoC.

Not yet fully implemented:

* richer technical formula engine,
* data-driven order code templates stored in DB,
* advanced grouped rule logic (AND/OR),
* staging-based ingestion pipeline,
* full production observability,
* deployment hardening end-to-end,
* approval workflow for quotes,
* advanced concurrency-safe business numbering.

---

## Mapping to the recruitment task

This PoC covers the most important parts of the task:

### Covered well

* architecture for configurable HVAC products,
* scalable data model,
* data-driven product definition,
* support for multiple product families,
* handling of variants and configuration dependencies,
* approach to ingestion from PDF/Excel,
* simple but real PoC backend.

### Covered partially / intentionally simplified

* technical calculations are demonstrated on a simplified example,
* order code generation is implemented in a simple family-based way,
* ingestion is described and partially represented through demo seeding rather than a full automated pipeline.

### Not yet fully implemented

* broader portfolio coverage beyond demo families,
* advanced formula engine,
* production-grade ingestion workflow.

A more recruitment-focused summary is available in [`docs/recruitment-submission.md`](docs/recruitment-submission.md).

---

## Documentation index

* [`CLAUDE.md`](CLAUDE.md) — high-signal project guide
* [`docs/architecture.md`](docs/architecture.md) — architecture overview
* [`docs/erd.md`](docs/erd.md) — ERD and data model
* [`docs/data-ingestion.md`](docs/data-ingestion.md) — ingestion approach
* [`docs/demo-families.md`](docs/demo-families.md) — demo family descriptions
* [`docs/recruitment-submission.md`](docs/recruitment-submission.md) — task-oriented summary

---

## Next steps

The most valuable next improvements are:

1. integrate technical calculation results into quote snapshots,
2. move order code generation toward DB-driven templates,
3. expand technical calculation engine,
4. add stronger migration-based test setup,
5. improve observability and deployment hardening,
6. expand demo data toward more HVAC categories.
