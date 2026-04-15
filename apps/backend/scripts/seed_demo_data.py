"""Demo seed data — showcases all CPQ system capabilities.

Each product family demonstrates different features:
  - fire_damper_rectangular: all attribute types (INTEGER, ENUM, BOOLEAN, DECIMAL),
    all rule types (REQUIRES, FORBIDS, RESTRICTS), rich pricing
  - fire_damper_round: alternative geometry, GT/LT operators, unique connection attribute
  - multi_blade_fire_damper: complex multi-rule interactions, premium options, BOOLEAN motorized
"""

from decimal import Decimal

from app.db.session import SessionLocal
from app.db.models import (
    AttributeDefinitionModel,
    AttributeOptionModel,
    AttributeType,
    ProductFamilyModel,
    ProductPricingRuleModel,
    ProductRuleModel,
    PricingRuleType,
    RuleOperator,
    RuleType,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def add_enum_attribute(
    family: ProductFamilyModel,
    *,
    code: str,
    name: str,
    options: list[str],
    is_required: bool = False,
    description: str | None = None,
) -> None:
    attribute = AttributeDefinitionModel(
        code=code,
        name=name,
        attribute_type=AttributeType.ENUM,
        is_required=is_required,
        description=description,
    )
    for index, option in enumerate(options, start=1):
        attribute.enum_options.append(
            AttributeOptionModel(value=option, label=option, sort_order=index)
        )
    family.attributes.append(attribute)


def add_integer_attribute(
    family: ProductFamilyModel,
    *,
    code: str,
    name: str,
    min_int: int,
    max_int: int,
    unit: str = "mm",
    is_required: bool = False,
    description: str | None = None,
) -> None:
    family.attributes.append(
        AttributeDefinitionModel(
            code=code,
            name=name,
            attribute_type=AttributeType.INTEGER,
            is_required=is_required,
            unit=unit,
            min_int=min_int,
            max_int=max_int,
            description=description,
        )
    )


def add_decimal_attribute(
    family: ProductFamilyModel,
    *,
    code: str,
    name: str,
    min_decimal: Decimal,
    max_decimal: Decimal,
    unit: str | None = None,
    is_required: bool = False,
    description: str | None = None,
) -> None:
    family.attributes.append(
        AttributeDefinitionModel(
            code=code,
            name=name,
            attribute_type=AttributeType.DECIMAL,
            is_required=is_required,
            unit=unit,
            min_decimal=min_decimal,
            max_decimal=max_decimal,
            description=description,
        )
    )


def add_boolean_attribute(
    family: ProductFamilyModel,
    *,
    code: str,
    name: str,
    is_required: bool = False,
    description: str | None = None,
) -> None:
    family.attributes.append(
        AttributeDefinitionModel(
            code=code,
            name=name,
            attribute_type=AttributeType.BOOLEAN,
            is_required=is_required,
            description=description,
        )
    )


# ---------------------------------------------------------------------------
# Family 1: Rectangular Fire Damper — full feature showcase
# ---------------------------------------------------------------------------

def seed_rectangular_fire_damper() -> ProductFamilyModel:
    """Demonstrates ALL attribute types, ALL rule types, and rich pricing logic."""

    family = ProductFamilyModel(
        code="fire_damper_rectangular",
        name="Fire Damper Rectangular",
        description="Rectangular fire damper for standard HVAC duct systems. "
                    "Available in multiple fire classes with optional thermal insulation.",
        is_active=True,
    )

    # --- Attributes (7 total — INTEGER, ENUM, BOOLEAN, DECIMAL) ---

    add_integer_attribute(
        family, code="width", name="Width",
        min_int=200, max_int=2000, is_required=True,
        description="Internal clear width of the damper opening",
    )
    add_integer_attribute(
        family, code="height", name="Height",
        min_int=200, max_int=1500, is_required=True,
        description="Internal clear height of the damper opening",
    )
    add_enum_attribute(
        family, code="fire_class", name="Fire Class",
        options=["EI30", "EI60", "EI120"], is_required=True,
        description="Fire resistance classification per EN 13501-3",
    )
    add_enum_attribute(
        family, code="actuator_type", name="Actuator Type",
        options=["standard", "reinforced", "spring_return"], is_required=False,
        description="Actuator mechanism for damper blade operation",
    )
    add_enum_attribute(
        family, code="installation_type", name="Installation Type",
        options=["wall", "ceiling", "floor"], is_required=False,
        description="Mounting position in the building structure",
    )
    add_boolean_attribute(
        family, code="thermal_insulation", name="Thermal Insulation",
        is_required=False,
        description="Add external thermal insulation casing to prevent condensation",
    )
    add_decimal_attribute(
        family, code="insulation_thickness", name="Insulation Thickness",
        min_decimal=Decimal("20.0"), max_decimal=Decimal("100.0"),
        unit="mm", is_required=False,
        description="Thickness of the thermal insulation layer",
    )

    # --- Business Rules (5 — all 3 rule types, EQ + GT operators) ---

    family.rules.extend([
        # REQUIRES_ATTRIBUTE + EQ: high fire class needs actuator
        ProductRuleModel(
            name="EI120 requires actuator",
            rule_type=RuleType.REQUIRES_ATTRIBUTE,
            if_attribute_code="fire_class",
            operator=RuleOperator.EQ,
            expected_value="EI120",
            target_attribute_code="actuator_type",
            error_message="Actuator type is required for EI120 fire class.",
            is_active=True,
        ),
        # FORBIDS_ATTRIBUTE + EQ: lowest fire class cannot have insulation
        ProductRuleModel(
            name="EI30 forbids thermal insulation",
            rule_type=RuleType.FORBIDS_ATTRIBUTE,
            if_attribute_code="fire_class",
            operator=RuleOperator.EQ,
            expected_value="EI30",
            target_attribute_code="thermal_insulation",
            error_message="Thermal insulation is not available for EI30 fire class.",
            is_active=True,
        ),
        # RESTRICTS_VALUE + EQ: ceiling limits actuator choices
        ProductRuleModel(
            name="Ceiling restricts actuator types",
            rule_type=RuleType.RESTRICTS_VALUE,
            if_attribute_code="installation_type",
            operator=RuleOperator.EQ,
            expected_value="ceiling",
            target_attribute_code="actuator_type",
            allowed_values=["standard", "spring_return"],
            error_message="Only standard and spring-return actuators are allowed for ceiling installation (reinforced is too heavy).",
            is_active=True,
        ),
        # REQUIRES_ATTRIBUTE + GT: large dampers need actuator
        ProductRuleModel(
            name="Large width requires actuator",
            rule_type=RuleType.REQUIRES_ATTRIBUTE,
            if_attribute_code="width",
            operator=RuleOperator.GT,
            expected_value="1500",
            target_attribute_code="actuator_type",
            error_message="Actuator type is required for dampers wider than 1500 mm.",
            is_active=True,
        ),
    ])

    # --- Pricing Rules (6 — base + fixed + percentage surcharges) ---

    family.pricing_rules.extend([
        ProductPricingRuleModel(
            name="Base price rectangular",
            pricing_rule_type=PricingRuleType.BASE_PRICE,
            amount=Decimal("500.00"),
            currency="PLN",
            label="Base price",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="EI120 fire class surcharge",
            pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
            if_attribute_code="fire_class",
            operator=RuleOperator.EQ,
            expected_value="EI120",
            amount=Decimal("200.00"),
            currency="PLN",
            label="EI120 fire class surcharge",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Large width surcharge",
            pricing_rule_type=PricingRuleType.PERCENTAGE_SURCHARGE,
            if_attribute_code="width",
            operator=RuleOperator.GT,
            expected_value="1200",
            amount=Decimal("15.00"),
            currency="PLN",
            label="Oversize width surcharge (>1200 mm)",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Large height surcharge",
            pricing_rule_type=PricingRuleType.PERCENTAGE_SURCHARGE,
            if_attribute_code="height",
            operator=RuleOperator.GT,
            expected_value="1000",
            amount=Decimal("10.00"),
            currency="PLN",
            label="Oversize height surcharge (>1000 mm)",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Thermal insulation surcharge",
            pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
            if_attribute_code="thermal_insulation",
            operator=RuleOperator.EQ,
            expected_value="True",
            amount=Decimal("150.00"),
            currency="PLN",
            label="Thermal insulation casing",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Reinforced actuator surcharge",
            pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
            if_attribute_code="actuator_type",
            operator=RuleOperator.EQ,
            expected_value="reinforced",
            amount=Decimal("120.00"),
            currency="PLN",
            label="Reinforced actuator upgrade",
            is_active=True,
        ),
    ])

    return family


# ---------------------------------------------------------------------------
# Family 2: Round Fire Damper — alternative geometry + unique connection type
# ---------------------------------------------------------------------------

def seed_round_fire_damper() -> ProductFamilyModel:
    """Demonstrates different dimension model (diameter), GT/LT operators, unique attributes."""

    family = ProductFamilyModel(
        code="fire_damper_round",
        name="Fire Damper Round",
        description="Round fire damper for circular duct systems. "
                    "Compact design with multiple connection options.",
        is_active=True,
    )

    # --- Attributes (5 total) ---

    add_integer_attribute(
        family, code="diameter", name="Diameter",
        min_int=100, max_int=1000, is_required=True,
        description="Internal clear diameter of the circular opening",
    )
    add_enum_attribute(
        family, code="fire_class", name="Fire Class",
        options=["EI60", "EI120"], is_required=True,
        description="Fire resistance classification per EN 13501-3",
    )
    add_enum_attribute(
        family, code="actuator_type", name="Actuator Type",
        options=["standard", "reinforced"], is_required=False,
        description="Actuator mechanism for damper blade operation",
    )
    add_enum_attribute(
        family, code="connection_type", name="Connection Type",
        options=["flange", "sleeve", "spigot"], is_required=False,
        description="Duct connection method (flange for rigid, sleeve for flexible, spigot for push-fit)",
    )
    add_enum_attribute(
        family, code="installation_type", name="Installation Type",
        options=["wall", "ceiling"], is_required=False,
        description="Mounting position in the building structure",
    )

    # --- Business Rules (3 — EQ, GT, LT operators) ---

    family.rules.extend([
        # REQUIRES_ATTRIBUTE + EQ
        ProductRuleModel(
            name="EI120 requires actuator",
            rule_type=RuleType.REQUIRES_ATTRIBUTE,
            if_attribute_code="fire_class",
            operator=RuleOperator.EQ,
            expected_value="EI120",
            target_attribute_code="actuator_type",
            error_message="Actuator type is required for EI120 fire class.",
            is_active=True,
        ),
        # FORBIDS_ATTRIBUTE + GT: large diameter cannot use sleeve
        ProductRuleModel(
            name="Large diameter forbids sleeve connection",
            rule_type=RuleType.FORBIDS_ATTRIBUTE,
            if_attribute_code="diameter",
            operator=RuleOperator.GT,
            expected_value="600",
            target_attribute_code="connection_type",
            error_message="Sleeve connection is not available for dampers with diameter above 600 mm. Use flange or spigot instead.",
            is_active=True,
        ),
        # RESTRICTS_VALUE + LT: small diameter limits actuator
        ProductRuleModel(
            name="Small diameter restricts actuator",
            rule_type=RuleType.RESTRICTS_VALUE,
            if_attribute_code="diameter",
            operator=RuleOperator.LT,
            expected_value="200",
            target_attribute_code="actuator_type",
            allowed_values=["standard"],
            error_message="Only standard actuator fits dampers with diameter below 200 mm.",
            is_active=True,
        ),
    ])

    # --- Pricing Rules (4) ---

    family.pricing_rules.extend([
        ProductPricingRuleModel(
            name="Base price round",
            pricing_rule_type=PricingRuleType.BASE_PRICE,
            amount=Decimal("450.00"),
            currency="PLN",
            label="Base price",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="EI120 fire class surcharge",
            pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
            if_attribute_code="fire_class",
            operator=RuleOperator.EQ,
            expected_value="EI120",
            amount=Decimal("180.00"),
            currency="PLN",
            label="EI120 fire class surcharge",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Large diameter surcharge",
            pricing_rule_type=PricingRuleType.PERCENTAGE_SURCHARGE,
            if_attribute_code="diameter",
            operator=RuleOperator.GT,
            expected_value="600",
            amount=Decimal("10.00"),
            currency="PLN",
            label="Oversize diameter surcharge (>600 mm)",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Flange connection surcharge",
            pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
            if_attribute_code="connection_type",
            operator=RuleOperator.EQ,
            expected_value="flange",
            amount=Decimal("80.00"),
            currency="PLN",
            label="Flange connection upgrade",
            is_active=True,
        ),
    ])

    return family


# ---------------------------------------------------------------------------
# Family 3: Multi Blade Fire Damper — complex product with many rules
# ---------------------------------------------------------------------------

def seed_multi_blade_fire_damper() -> ProductFamilyModel:
    """Demonstrates complex rule interactions, premium material options, and BOOLEAN motorized."""

    family = ProductFamilyModel(
        code="multi_blade_fire_damper",
        name="Multi Blade Fire Damper",
        description="Multi-blade fire damper for larger ventilation openings. "
                    "Suitable for high-volume air handling systems with optional motorization.",
        is_active=True,
    )

    # --- Attributes (7 total) ---

    add_integer_attribute(
        family, code="width", name="Width",
        min_int=300, max_int=2500, is_required=True,
        description="Internal clear width of the damper opening",
    )
    add_integer_attribute(
        family, code="height", name="Height",
        min_int=300, max_int=2000, is_required=True,
        description="Internal clear height of the damper opening",
    )
    add_enum_attribute(
        family, code="fire_class", name="Fire Class",
        options=["EI60", "EI120"], is_required=True,
        description="Fire resistance classification per EN 13501-3",
    )
    add_enum_attribute(
        family, code="blade_type", name="Blade Type",
        options=["standard", "insulated", "low_leakage"], is_required=True,
        description="Blade construction type — standard, thermally insulated, or low-leakage rated",
    )
    add_enum_attribute(
        family, code="installation_type", name="Installation Type",
        options=["wall", "ceiling"], is_required=False,
        description="Mounting position in the building structure",
    )
    add_enum_attribute(
        family, code="frame_material", name="Frame Material",
        options=["galvanized_steel", "stainless_steel"], is_required=False,
        description="Frame and casing material grade",
    )
    add_boolean_attribute(
        family, code="motorized", name="Motorized",
        is_required=False,
        description="Electric motor actuator for automated BMS integration",
    )

    # --- Business Rules (4 — complex interactions) ---

    family.rules.extend([
        # RESTRICTS_VALUE: EI120 needs insulated or low-leakage blades
        ProductRuleModel(
            name="EI120 restricts blade type",
            rule_type=RuleType.RESTRICTS_VALUE,
            if_attribute_code="fire_class",
            operator=RuleOperator.EQ,
            expected_value="EI120",
            target_attribute_code="blade_type",
            allowed_values=["insulated", "low_leakage"],
            error_message="EI120 fire class requires insulated or low-leakage blades.",
            is_active=True,
        ),
        # REQUIRES_ATTRIBUTE + GT: very large dampers need motor
        ProductRuleModel(
            name="Large damper requires motorization",
            rule_type=RuleType.REQUIRES_ATTRIBUTE,
            if_attribute_code="width",
            operator=RuleOperator.GT,
            expected_value="1800",
            target_attribute_code="motorized",
            error_message="Motorization is required for dampers wider than 1800 mm.",
            is_active=True,
        ),
        # RESTRICTS_VALUE: low-leakage blade needs stainless steel frame
        ProductRuleModel(
            name="Low-leakage requires stainless steel",
            rule_type=RuleType.RESTRICTS_VALUE,
            if_attribute_code="blade_type",
            operator=RuleOperator.EQ,
            expected_value="low_leakage",
            target_attribute_code="frame_material",
            allowed_values=["stainless_steel"],
            error_message="Low-leakage blades require a stainless steel frame for proper sealing.",
            is_active=True,
        ),
        # FORBIDS_ATTRIBUTE: ceiling mount cannot have motorization
        ProductRuleModel(
            name="Ceiling forbids motorization",
            rule_type=RuleType.FORBIDS_ATTRIBUTE,
            if_attribute_code="installation_type",
            operator=RuleOperator.EQ,
            expected_value="ceiling",
            target_attribute_code="motorized",
            error_message="Motorized actuator is not available for ceiling installation due to weight constraints.",
            is_active=True,
        ),
    ])

    # --- Pricing Rules (6 — multiple fixed + percentage surcharges) ---

    family.pricing_rules.extend([
        ProductPricingRuleModel(
            name="Base price multi blade",
            pricing_rule_type=PricingRuleType.BASE_PRICE,
            amount=Decimal("700.00"),
            currency="PLN",
            label="Base price",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="EI120 fire class surcharge",
            pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
            if_attribute_code="fire_class",
            operator=RuleOperator.EQ,
            expected_value="EI120",
            amount=Decimal("250.00"),
            currency="PLN",
            label="EI120 fire class surcharge",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Insulated blade surcharge",
            pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
            if_attribute_code="blade_type",
            operator=RuleOperator.EQ,
            expected_value="insulated",
            amount=Decimal("120.00"),
            currency="PLN",
            label="Insulated blade surcharge",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Low-leakage blade surcharge",
            pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
            if_attribute_code="blade_type",
            operator=RuleOperator.EQ,
            expected_value="low_leakage",
            amount=Decimal("200.00"),
            currency="PLN",
            label="Low-leakage blade premium",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Stainless steel frame surcharge",
            pricing_rule_type=PricingRuleType.PERCENTAGE_SURCHARGE,
            if_attribute_code="frame_material",
            operator=RuleOperator.EQ,
            expected_value="stainless_steel",
            amount=Decimal("25.00"),
            currency="PLN",
            label="Stainless steel frame upgrade (+25%)",
            is_active=True,
        ),
        ProductPricingRuleModel(
            name="Motorization surcharge",
            pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
            if_attribute_code="motorized",
            operator=RuleOperator.EQ,
            expected_value="True",
            amount=Decimal("350.00"),
            currency="PLN",
            label="Electric motor actuator",
            is_active=True,
        ),
    ])

    return family


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    session = SessionLocal()
    try:
        existing_codes = {
            row[0]
            for row in session.query(ProductFamilyModel.code).all()
        }

        families_to_seed = [
            seed_rectangular_fire_damper(),
            seed_round_fire_damper(),
            seed_multi_blade_fire_damper(),
        ]

        seeded = 0
        for family in families_to_seed:
            if family.code in existing_codes:
                print(f"  SKIP  {family.code} (already exists)")
                continue
            session.add(family)
            attr_count = len(family.attributes)
            rule_count = len(family.rules)
            pricing_count = len(family.pricing_rules)
            print(f"  SEED  {family.code} ({attr_count} attrs, {rule_count} rules, {pricing_count} pricing)")
            seeded += 1

        session.commit()
        print(f"\nDone. Seeded {seeded} new families ({len(existing_codes)} already existed).")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
