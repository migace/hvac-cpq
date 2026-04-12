# Architecture

## Purpose

This project is a **data-driven CPQ backend PoC for HVAC manufacturers**.

The initial implementation focuses on fire dampers, but the architecture is intended to scale to:
- multiple HVAC categories,
- multiple product families,
- dynamic product parameters,
- family-specific business rules,
- family-specific pricing logic,
- technical calculations,
- offer generation.

---

## Architectural style

The project follows a layered architecture with explicit separation of concerns.

### API layer
Responsible for:
- FastAPI routes,
- request/response schemas,
- dependency injection,
- mapping exceptions to HTTP responses.

### Service layer
Responsible for:
- orchestration of business use cases,
- configuration validation flow,
- rule execution,
- price calculation,
- order code generation,
- technical calculations,
- quote generation.

### Domain layer
Responsible for:
- business semantics,
- domain exceptions,
- product configuration rules and constraints.

### Repository layer
Responsible for:
- SQLAlchemy query encapsulation,
- entity loading with correct relationships,
- persistence access patterns.

### Persistence layer
Responsible for:
- ORM models,
- schema structure,
- DB sessions,
- migrations.

### Cross-cutting concerns
Responsible for:
- logging,
- request correlation,
- error formatting,
- observability integration points.

---

## Why this architecture

The main business problem is not just storing products. The system must support:
- dynamic product structures,
- different families with different attributes,
- rule-based validation,
- rule-based pricing,
- business outputs like quote and order code.

Because of that:
- product definition must be data-driven,
- configuration storage must be flexible,
- validation and pricing must be separated from storage,
- quotes must preserve historical business state.

---

## Main business flow

### 1. Define product family
A product family defines:
- available attributes,
- enum options,
- required vs optional fields,
- rules,
- pricing rules.

### 2. Create configuration
A user creates a product configuration by selecting values for family attributes.

### 3. Validate configuration
Validation happens in layers:
- request payload validation,
- required attribute validation,
- value type/range/enum validation,
- business rule validation.

### 4. Calculate price
Pricing is calculated using family pricing rules:
- exactly one base price,
- optional surcharges,
- final price breakdown.

### 5. Generate outputs
The system can additionally:
- generate order code,
- calculate technical parameters,
- create a quote.

### 6. Persist quote
The quote stores:
- historical configuration snapshot,
- historical pricing snapshot,
- final price values,
- quote number and status.

---

## Why EAV is used here

EAV is used for **configuration values**, not for the whole system.

### EAV is used for:
- dynamic product configurations,
- families with different sets of attributes,
- avoiding schema change for every new parameter.

### EAV is not used for:
- rules,
- pricing,
- quote snapshot,
- overall business orchestration.

This keeps the model flexible without turning everything into generic metadata.

---

## Why rules are modeled separately

Rules are stored separately from EAV because:
- EAV stores values,
- rules define meaning and constraints.

Examples:
- if `fire_class = EI120`, `actuator_type` is required,
- if `shape = round`, `height` is forbidden.

Keeping rules separate makes the system:
- easier to maintain,
- easier to extend,
- closer to real CPQ behavior.

---

## Why pricing is modeled separately

Pricing is a separate concern because:
- validation and pricing evolve differently,
- one family may stay valid while pricing changes,
- business users need breakdown and explanation.

The pricing engine currently supports:
- base price,
- fixed surcharge,
- percentage surcharge.

---

## Why quotes store snapshots

A quote must represent the state of the system at the time it was generated.

If pricing or rules change later, an already generated quote should still preserve:
- original configuration,
- original price breakdown,
- original final total.

That is why quotes store:
- `configuration_snapshot`
- `pricing_snapshot`

This is essential for business correctness.

---

## Technical calculation philosophy

Technical calculations are intentionally separated from:
- rules,
- pricing,
- persistence.

This allows future extension toward:
- product sizing logic,
- engineering formulas,
- automatic variant selection,
- more advanced HVAC calculations.

The current PoC includes effective area calculation for:
- rectangular fire dampers,
- round fire dampers.

---

## Order code philosophy

Order code generation is treated as a business output, not as a storage concern.

The current PoC:
- uses family-specific prefixes,
- uses selected configuration attributes,
- builds deterministic order codes.

In the future this can evolve into:
- templated order code definitions,
- configurable segment mapping,
- family-specific code schemas stored in DB.

---

## Repository design

Repositories are used to:
- centralize query patterns,
- prevent duplicated `selectinload(...)` logic,
- keep services focused on business behavior.

This is especially useful because the domain often requires loading:
- family + attributes + rules + pricing rules,
- configuration + values + attribute definitions,
- quote + snapshots.

---

## Error handling strategy

The system distinguishes between:
- request validation errors,
- domain errors,
- database errors,
- unexpected internal errors.

The API returns a consistent error shape with:
- `type`
- `message`
- `code`
- `request_id`
- optional `details`

This improves:
- frontend integration,
- observability,
- API test stability.

---

## Current strengths

The current PoC already demonstrates:
- a scalable product family model,
- configurable products with dynamic attributes,
- explicit business rules,
- explicit pricing rules,
- technical output generation,
- order code generation,
- quote snapshot persistence.

This is the current CPQ core of the project.

---

## Current limitations

The project is still a PoC.

Not yet implemented:
- full formula engine,
- data-driven order code templates,
- staging-based ingestion pipeline,
- advanced grouped rules,
- approval workflows,
- richer observability,
- deployment hardening end-to-end.