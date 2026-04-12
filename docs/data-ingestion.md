# Data ingestion approach

## Goal

The goal of data ingestion is to transform fragmented HVAC product knowledge from:
- PDF catalogs,
- Excel sheets,
- legacy HTML tools,
- internal expert knowledge,

into a structured CPQ data model that can be used for:
- configuration,
- validation,
- pricing,
- technical calculations,
- quote generation.

---

## Core principle

PDF and Excel should not be treated as the long-term source of truth.

They should be treated as:
- source materials,
- carriers of product knowledge,
- inputs to normalization and extraction.

The structured PostgreSQL CPQ model should become the operational source of truth.

---

## Proposed ingestion pipeline

### 1. Source inventory
Collect source materials for one category, for example fire dampers:
- catalog PDFs,
- technical sheets,
- dimension tables,
- fire resistance data,
- accessory tables,
- internal Excel sheets,
- legacy configurators.

Goal:
- identify product families,
- identify repeatable attributes,
- identify explicit and implicit business rules,
- identify pricing sources.

---

### 2. Domain decomposition
The source material should not be imported 1:1.

Instead, the knowledge should be decomposed into:
- product families,
- attribute definitions,
- enum options,
- business rules,
- pricing rules,
- technical formulas.

This is the most important transformation step.

---

### 3. Staging layer
Before importing into the final CPQ schema, use a staging layer.

Examples:
- staging tables,
- normalized JSON files,
- curated CSV/YAML files.

The staging layer helps:
- validate source quality,
- standardize naming,
- resolve inconsistencies,
- review extracted structures.

---

### 4. Normalization
Normalize:
- attribute names,
- units,
- enum values,
- family codes,
- dimension naming,
- accessory names.

Examples:
- `Width`, `Szerokość`, `B` → `width`
- `Height`, `Wysokość`, `H` → `height`
- `EI 120`, `EI120` → `EI120`

Without normalization, the CPQ model becomes inconsistent very quickly.

---

### 5. Validation before import
Before final import, validate:
- required family structure exists,
- enum attributes have options,
- numeric ranges are valid,
- rules reference existing attributes,
- pricing has exactly one active base price,
- sample configurations can be created successfully.

This can be implemented as:
- import validation scripts,
- Pydantic validation,
- test fixtures,
- pre-import checks.

---

### 6. Import into CPQ model
After normalization and validation, import data into:
- `product_families`
- `attribute_definitions`
- `attribute_options`
- `product_rules`
- `product_pricing_rules`

At this point the source material has been transformed into a usable application model.

---

## Recommended approach for the PoC

For this recruitment PoC, the best approach is **semi-manual ingestion**:
1. review a small set of product cards/catalog pages,
2. extract normalized family and attribute structures manually,
3. store them in seed/demo scripts or curated JSON/CSV,
4. import them into PostgreSQL.

### Why this is the best PoC choice
- it focuses on modeling quality,
- it avoids wasting time on unreliable PDF parsing,
- it shows domain thinking,
- it is realistic and honest.

---

## Recommended future direction

For a more mature version:
- add staging tables,
- add import validation CLI,
- optionally add assisted PDF/table extraction,
- keep human review in the loop,
- version source imports and normalized outputs.

A fully automatic parser should not be the first assumption in HVAC product onboarding.

---

## Main design insight

The hardest part is not storing data in PostgreSQL.

The hardest part is transforming product knowledge from heterogeneous documents into:
- normalized families,
- consistent attributes,
- rules,
- pricing,
- technical logic.

That is why ingestion should be treated as a **domain modeling problem**, not just as file parsing.
