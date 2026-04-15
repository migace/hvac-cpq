# Current feature scope

## 1. Product family modeling
- create product families,
- define dynamic attributes,
- support multiple attribute types,
- define enum options,
- mark attributes as required,
- define numeric ranges and units.

## 2. EAV configuration storage
- create a product configuration,
- store selected values in EAV form,
- support `string`, `integer`, `decimal`, `boolean`, and `enum` values,
- validate attribute existence and value type.

## 3. Complete configuration validation
- reject empty configurations,
- reject missing required attributes,
- reject unknown attribute codes,
- reject invalid enum/range/type combinations.

## 4. Business rules engine
Supports rule types: `requires_attribute`, `forbids_attribute`, `restricts_value`.

Supports condition operators: `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`.

## 5. Pricing engine
Supports pricing rule types: `base_price`, `fixed_surcharge`, `percentage_surcharge`.

Returns: currency, base price, surcharge total, final price, price breakdown.

## 6. Quote generation
- quote creation for an existing configuration,
- quote number generation,
- quote status,
- historical configuration snapshot (immutable),
- historical pricing snapshot (immutable).

## 7. Order code generation
Simple family-specific order code generation for selected fire damper families.

## 8. Technical calculations
Example technical calculations such as effective area for rectangular and round fire dampers.

## 9. AI product advisor
- natural language product search and configuration,
- tool-calling agent with 6 tools (search, details, price, validate, order code, technical),
- SSE streaming responses,
- automatic form population from AI suggestions,
- observability metrics (tokens, latency, cost).

## 10. Demo data seeding
Seeding of demo families:
- `fire_damper_rectangular`,
- `fire_damper_round`,
- `multi_blade_fire_damper`.

## 11. Frontend configurator
- product family selection,
- dynamic form generation from attribute definitions,
- real-time price calculation,
- order history,
- AI chat panel integrated with configurator.
