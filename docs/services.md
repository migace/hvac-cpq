# Services

## Overview

The backend uses a service layer to orchestrate business use cases. Services live in `apps/backend/app/services/`.

---

## Core domain services

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

Supports rule types: `requires_attribute`, `forbids_attribute`, `restricts_value`.

Supports condition operators: `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`.

### `PricingEngine`
Calculates price and returns structured breakdown.

Supports pricing rule types: `base_price`, `fixed_surcharge`, `percentage_surcharge`.

Returns: currency, base price, surcharge total, final price, price breakdown.

### `ProductQuoteService`
Creates quotes and stores pricing/configuration snapshots.

### `OrderCodeService`
Builds order codes based on family and selected configuration values.

Order codes are generated only for valid configurations (must pass payload validation, required attributes, and rules engine). The current PoC uses family prefix mapping, segment composition, and simple value-to-code mappings.

### `TechnicalCalculationService`
Computes selected technical outputs from valid configuration input.

Calculations are intentionally separated from rules, pricing, and persistence. The current PoC includes effective area calculation for rectangular and round fire dampers.

---

## AI agent services

### `AgentService`
Orchestrates the LLM conversation with a tool-calling loop. Located in `apps/backend/app/services/agent/service.py`.

Key characteristics:
- stateless — conversation history managed by the caller,
- streams SSE events via async generator,
- max 10 tool iterations per invocation,
- collects `AgentInvocationMetrics` (tokens, latency, cost, tools used).

### `AgentTools`
Thin wrappers that expose domain services to the LLM via tool calling. Located in `apps/backend/app/services/agent/tools.py`.

Available tools: `search_products`, `get_family_details`, `calculate_price`, `validate_configuration`, `generate_order_code`, `calculate_technical_params`.

No business logic lives here — tools are pure adapters.
