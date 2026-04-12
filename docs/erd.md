# ERD

## Overview

The data model is designed as a **data-driven CPQ core** for configurable HVAC products.

It separates:
- product family definition,
- attribute definition,
- concrete configuration values,
- business rules,
- pricing rules,
- historical business outputs.

---

## Main entities

### `product_families`
Defines a product family, for example:
- rectangular fire damper,
- round fire damper,
- multi-blade fire damper.

Important fields:
- `id`
- `code`
- `name`
- `description`
- `is_active`

---

### `attribute_definitions`
Defines attributes available for a product family.

Examples:
- width
- height
- diameter
- fire_class
- actuator_type
- installation_type
- blade_type

Important fields:
- `id`
- `product_family_id`
- `code`
- `name`
- `attribute_type`
- `is_required`
- `unit`
- numeric ranges

---

### `attribute_options`
Defines enum values for enum-type attributes.

Examples:
- EI60
- EI120
- standard
- reinforced
- wall
- ceiling

---

### `product_configurations`
Defines one concrete user-created configuration.

Important fields:
- `id`
- `product_family_id`
- `name`
- `status`

---

### `attribute_values`
Stores actual configuration values using the EAV pattern.

Important fields:
- `id`
- `configuration_id`
- `attribute_definition_id`
- `value_string`
- `value_integer`
- `value_decimal`
- `value_boolean`

---

### `product_rules`
Stores business validation rules for a family.

Important fields:
- `id`
- `product_family_id`
- `name`
- `rule_type`
- `if_attribute_code`
- `operator`
- `expected_value`
- `target_attribute_code`
- `allowed_values`
- `error_message`
- `is_active`

---

### `product_pricing_rules`
Stores pricing rules for a family.

Important fields:
- `id`
- `product_family_id`
- `name`
- `pricing_rule_type`
- `if_attribute_code`
- `operator`
- `expected_value`
- `amount`
- `currency`
- `label`
- `is_active`

---

### `product_quotes`
Stores generated offers with historical snapshots.

Important fields:
- `id`
- `product_configuration_id`
- `quote_number`
- `status`
- `currency`
- `base_price`
- `surcharge_total`
- `total_price`
- `configuration_snapshot`
- `pricing_snapshot`

---

## Relationship summary

- one `product_family` has many `attribute_definitions`
- one `product_family` has many `product_configurations`
- one `product_family` has many `product_rules`
- one `product_family` has many `product_pricing_rules`
- one `attribute_definition` has many `attribute_options`
- one `product_configuration` has many `attribute_values`
- one `attribute_definition` may be used in many `attribute_values`
- one `product_configuration` has many `product_quotes`

---

## Why this model

This model supports:
- many product families,
- different attribute sets per family,
- configuration without schema change for every new field,
- separated business validation and pricing logic,
- historical quotes.

---

## Mermaid ERD

```mermaid
erDiagram
    PRODUCT_FAMILIES ||--o{ ATTRIBUTE_DEFINITIONS : has
    PRODUCT_FAMILIES ||--o{ PRODUCT_CONFIGURATIONS : has
    PRODUCT_FAMILIES ||--o{ PRODUCT_RULES : has
    PRODUCT_FAMILIES ||--o{ PRODUCT_PRICING_RULES : has

    ATTRIBUTE_DEFINITIONS ||--o{ ATTRIBUTE_OPTIONS : has
    ATTRIBUTE_DEFINITIONS ||--o{ ATTRIBUTE_VALUES : used_in

    PRODUCT_CONFIGURATIONS ||--o{ ATTRIBUTE_VALUES : contains
    PRODUCT_CONFIGURATIONS ||--o{ PRODUCT_QUOTES : generates

    PRODUCT_FAMILIES {
        int id PK
        string code
        string name
        text description
        bool is_active
    }

    ATTRIBUTE_DEFINITIONS {
        int id PK
        int product_family_id FK
        string code
        string name
        string attribute_type
        bool is_required
        string unit
        int min_int
        int max_int
        decimal min_decimal
        decimal max_decimal
    }

    ATTRIBUTE_OPTIONS {
        int id PK
        int attribute_definition_id FK
        string value
        string label
        int sort_order
    }

    PRODUCT_CONFIGURATIONS {
        int id PK
        int product_family_id FK
        string name
        string status
    }

    ATTRIBUTE_VALUES {
        int id PK
        int configuration_id FK
        int attribute_definition_id FK
        string value_string
        int value_integer
        decimal value_decimal
        bool value_boolean
    }

    PRODUCT_RULES {
        int id PK
        int product_family_id FK
        string name
        string rule_type
        string if_attribute_code
        string operator
        string expected_value
        string target_attribute_code
        text allowed_values
        text error_message
        bool is_active
    }

    PRODUCT_PRICING_RULES {
        int id PK
        int product_family_id FK
        string name
        string pricing_rule_type
        string if_attribute_code
        string operator
        string expected_value
        decimal amount
        string currency
        string label
        bool is_active
    }

    PRODUCT_QUOTES {
        int id PK
        int product_configuration_id FK
        string quote_number
        string status
        string currency
        decimal base_price
        decimal surcharge_total
        decimal total_price
        json configuration_snapshot
        json pricing_snapshot
    }