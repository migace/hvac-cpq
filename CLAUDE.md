# CLAUDE.md

## Project overview

This repository contains a **data-driven CPQ PoC for HVAC products** implemented in **Python** with **FastAPI**, **SQLAlchemy 2.x**, **PostgreSQL**, and **Alembic**.

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

## Business context

HVAC manufacturers typically have:
- many product families,
- multiple variants per family,
- many configuration options,
- business constraints between parameters,
- pricing logic depending on selected options,
- product knowledge distributed across PDFs, Excel files, legacy tools, and expert knowledge.

This project addresses that by building a **single CPQ-oriented backend core** where:
- a product family defines the structure of a configurable product,
- attribute definitions describe available parameters,
- configurations store concrete user selections,
- rules validate allowed combinations,
- pricing rules calculate price,
- technical calculation services compute selected technical outputs,
- quotes persist historical pricing and configuration snapshots.

---

## High-level architecture

The project uses a layered architecture.

### API layer
Responsible for:
- FastAPI routes,
- request/response schemas,
- dependency injection,
- HTTP error mapping.

### Service layer
Responsible for:
- orchestration of use cases,
- validation flow,
- rule evaluation,
- pricing calculation,
- order code generation,
- technical calculations,
- quote generation.

### Domain layer
Responsible for:
- domain exceptions,
- business rules and constraints,
- semantic meaning of product configuration.

### Repository layer
Responsible for:
- fetching and storing ORM entities,
- encapsulating common SQLAlchemy query patterns,
- loading related entities consistently.

### Persistence layer
Responsible for:
- SQLAlchemy ORM models,
- PostgreSQL schema,
- Alembic migrations,
- DB session lifecycle.

### Cross-cutting concerns
Responsible for:
- structured logging,
- request correlation,
- error formatting,
- observability hooks.

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

### Core entities

#### `ProductFamily`
Represents one product family, for example:
- rectangular fire damper,
- round fire damper,
- multi-blade fire damper.

#### `AttributeDefinition`
Represents a dynamic attribute belonging to a product family.
Examples:
- width,
- height,
- diameter,
- fire_class,
- actuator_type,
- installation_type,
- blade_type.

#### `AttributeOption`
Represents enum values available for enum-type attributes.

#### `ProductConfiguration`
Represents one concrete product configuration built by a user.

#### `AttributeValue`
Represents a concrete selected value for one attribute in one configuration.
This is the actual EAV layer.

#### `ProductRule`
Represents business validation rules between attributes.

#### `ProductPricingRule`
Represents pricing logic for a family.

#### `ProductQuote`
Represents a generated business offer with historical snapshots.

---

## Data model summary

Main tables:
- `product_families`
- `attribute_definitions`
- `attribute_options`
- `product_configurations`
- `attribute_values`
- `product_rules`
- `product_pricing_rules`
- `product_quotes`

### Important design decisions

#### EAV is used only where it makes sense
EAV is used for **configuration values**, not for every aspect of the domain.

#### Rules are not embedded in EAV
Business logic is modeled separately in `product_rules`.

#### Pricing is modeled separately
Pricing is not mixed into configuration storage.

#### Quote stores snapshots
A quote stores historical configuration and pricing snapshots so that changes in rules or prices do not retroactively change old offers.

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

The project exposes API endpoints for:
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

The test setup is designed to keep application development data separate from test data.

### Current testing principles
- test DB must be isolated from dev DB,
- API tests should use dependency overrides,
- tests should validate both happy path and failure path,
- rules, pricing, order code generation, and technical calculations should be covered.

### Recommended direction
Use a dedicated PostgreSQL test container instead of SQLite when validating production-like behavior.

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

---

## Product data ingestion approach

This project assumes that HVAC product knowledge usually comes from:
- PDF catalogs,
- Excel sheets,
- legacy HTML tools,
- engineering know-how.

### Recommended ingestion pipeline
1. collect and inventory source materials,
2. extract product families and attribute knowledge,
3. normalize naming and units,
4. map to staging structures,
5. validate data quality,
6. import into CPQ data model.

### Important principle
PDF and Excel should be treated as **source materials**, not as the long-term source of truth.
The long-term source of truth should be the structured CPQ data model in PostgreSQL.

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

## Current architectural strengths

This project currently demonstrates:
- a data-driven approach,
- separation of product definition and configuration,
- support for dynamic attributes,
- explicit business rules,
- explicit pricing rules,
- historical quote snapshots,
- extensibility toward more HVAC categories and families.

These are the most important qualities of the current PoC.

---

## Known limitations / future improvements

The project is intentionally a PoC and does **not** yet implement the full production scope.

Examples of future improvements:
- richer formula engine for technical calculations,
- data-driven order code templates in DB,
- ingestion pipeline with staging tables,
- stronger migration-based DB testing,
- quote approval workflows,
- richer observability,
- metrics and tracing,
- deployment hardening,
- better handling of concurrency in quote number generation,
- support for more advanced rule composition (AND/OR, grouped conditions).

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

Recommended files:
- `docs/architecture.md`
- `docs/erd.md`
- `docs/data-ingestion.md`
- `docs/demo-families.md`
- `docs/recruitment-submission.md`

---

## Recommended next steps

The most valuable next improvements are:
1. move detailed architecture and ERD content into `docs/`,
2. integrate technical calculation results into quote snapshots,
3. improve demo flow documentation,
4. expand observability and deployment readiness,
5. prepare a polished recruitment-oriented README/submission summary.