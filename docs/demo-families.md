# Demo product families

## Purpose

The demo seed exists to show that the CPQ model is not hardcoded for a single product structure.

The PoC currently demonstrates 3 fire damper families:
- `fire_damper_rectangular`
- `fire_damper_round`
- `multi_blade_fire_damper`

Each family has:
- its own attribute set,
- its own rules,
- its own pricing rules,
- its own behavior for business outputs.

---

## 1. `fire_damper_rectangular`

### Business meaning
Rectangular fire damper for standard HVAC duct systems.

### Main attributes
- `width`
- `height`
- `fire_class`
- `actuator_type`
- `installation_type`

### Example use cases
- order code generation based on width/height,
- technical area calculation using width and height,
- pricing surcharge for high fire class,
- pricing surcharge for large width.

### Example business rules
- `EI120` requires `actuator_type`
- wall installation can restrict allowed actuator types

---

## 2. `fire_damper_round`

### Business meaning
Round fire damper for circular duct systems.

### Main attributes
- `diameter`
- `fire_class`
- `actuator_type`
- `installation_type`

### Why this family matters
It proves that the model does not assume rectangular dimensions only.

This family:
- does not use `width`
- does not use `height`
- uses `diameter` instead

### Example business rules
- `EI120` requires `actuator_type`

### Example technical calculations
- effective area based on diameter

---

## 3. `multi_blade_fire_damper`

### Business meaning
Multi-blade fire damper for larger or more complex ventilation openings.

### Main attributes
- `width`
- `height`
- `fire_class`
- `blade_type`
- `installation_type`

### Why this family matters
It shows that a third family can introduce a different product-specific attribute such as `blade_type`.

This proves that:
- family-specific logic is possible,
- the model can evolve with additional variants,
- rules are not tied to one attribute layout.

### Example business rules
- `EI120` requires `blade_type = insulated`

### Example pricing rules
- surcharge for `EI120`
- surcharge for insulated blade type

---

## Why these three families are useful

Together they demonstrate:
- different attribute sets,
- rectangular vs round dimension logic,
- different business rules,
- different pricing logic,
- extensibility of the CPQ core.

This is enough to show that the architecture is prepared for a broader HVAC product portfolio.