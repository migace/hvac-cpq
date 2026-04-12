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

This PoC implements a **data-driven CPQ backend core** for HVAC products using:
- Python
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Alembic

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

---

## Architecture summary

The system is structured into:
- API layer,
- service layer,
- domain layer,
- repository layer,
- persistence layer.

This separation keeps:
- data model flexible,
- validation explicit,
- pricing explicit,
- quote generation stable,
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
- historical quote persistence.

---

## Current limitations

This is intentionally still a PoC.

Not yet fully implemented:
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
- how I structure a scalable backend foundation,
- how I separate domain data, rules, pricing, and business outputs.

The solution is intentionally built as a strong architectural core that can be extended toward a full HVAC product selection platform.