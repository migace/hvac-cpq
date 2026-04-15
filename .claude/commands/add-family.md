Guide the user through adding a new HVAC product family following the 7-step checklist from CLAUDE.md. Generate all required code across the full stack.

## Context

This is a data-driven CPQ system. Product families are NOT hardcoded — they are defined via database records. Adding a new family means:
- Defining the family + attributes + options in seed data
- Adding business rules for valid combinations
- Adding pricing rules
- Optionally adding technical calculations
- No changes to route handlers or service logic should be needed (that's the point of the data-driven design)

## Input

Ask the user for the family details using the 7-step checklist. If the user provides a product datasheet, PDF, or description — extract the information from it.

## Step 1: Family identity

Ask or extract:
- `code` — unique snake_case identifier (e.g., `fire_damper_rectangular`)
- `name` — human-readable name (e.g., "Rectangular Fire Damper")
- `description` — brief product description

## Step 2: Attributes

For each attribute, determine:
- `code` — snake_case (e.g., `width`, `fire_class`)
- `name` — display name
- `attribute_type` — one of: STRING, INTEGER, DECIMAL, BOOLEAN, ENUM
- `is_required` — boolean
- `sort_order` — display ordering
- For INTEGER/DECIMAL: `min_value`, `max_value`
- For ENUM: list of options with `code`, `name`, `sort_order`

Reference existing families in `apps/backend/scripts/seed_demo_data.py` for patterns:
- fire_damper_rectangular: width, height, fire_class, actuator_type, installation_type
- fire_damper_round: diameter, fire_class, actuator_type, installation_type
- multi_blade_fire_damper: width, height, fire_class, blade_type, installation_type

## Step 3: Business rules

For each rule, define:
- `name` — business-readable rule name
- `rule_type` — REQUIRES_ATTRIBUTE, FORBIDS_ATTRIBUTE, or RESTRICTS_VALUE
- `condition_attribute` — which attribute triggers the rule
- `condition_operator` — EQ, NEQ, GT, GTE, LT, LTE, IN
- `condition_value` — trigger value
- `target_attribute` — affected attribute
- `target_operator` / `target_value` — constraint on target
- `error_message` — business-readable message shown on violation

## Step 4: Pricing rules

For each pricing rule:
- `name` — rule name
- `rule_type` — BASE_PRICE, FIXED_SURCHARGE, or PERCENTAGE_SURCHARGE
- `amount` — price amount (Decimal)
- `currency` — e.g., "PLN"
- `condition_attribute` / `condition_operator` / `condition_value` — optional conditional application
- Ensure exactly ONE BASE_PRICE rule exists

## Step 5: Order code pattern

Determine how the order code should be built from attribute values. Reference `apps/backend/app/services/order_code_service.py` for the existing pattern.

## Step 6: Technical calculations

Determine what formulas apply (e.g., effective area, weight, airflow). Reference `apps/backend/app/services/technical_calculation_service.py` for existing patterns.

## Step 7: Generate code

After gathering all information, generate:

1. **Seed data** — Add the new family to `apps/backend/scripts/seed_demo_data.py` following the exact pattern of existing families (create family → add attributes with options → add rules → add pricing rules)

2. **Tests** — Add tests in `apps/backend/tests/` that:
   - Create the family via API
   - Create a valid configuration
   - Test each business rule (valid + invalid cases)
   - Test pricing calculation
   - Test order code generation
   - Test technical calculations if applicable

3. **Documentation** — Update `docs/demo-families.md` with the new family's details

4. **Order code / technical calc** — If the new family needs custom order code logic or technical calculations not covered by existing generic logic, extend the respective services. But prefer data-driven over hardcoded.

## Important

- NEVER modify route handlers or service constructors for a new family — the architecture is data-driven
- Follow existing seed data patterns exactly — look at `seed_demo_data.py` before writing
- All attribute codes must be snake_case
- All error messages must be business-readable (not technical)
- Pricing must have exactly one BASE_PRICE rule
- Ask the user to confirm the plan before generating code
