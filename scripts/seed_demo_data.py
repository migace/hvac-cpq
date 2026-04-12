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


def add_enum_attribute(
    family: ProductFamilyModel,
    *,
    code: str,
    name: str,
    options: list[str],
    is_required: bool = False,
) -> None:
    attribute = AttributeDefinitionModel(
        code=code,
        name=name,
        attribute_type=AttributeType.ENUM,
        is_required=is_required,
    )
    for index, option in enumerate(options, start=1):
        attribute.enum_options.append(
            AttributeOptionModel(
                value=option,
                label=option,
                sort_order=index,
            )
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
        )
    )


def seed_rectangular_fire_damper() -> ProductFamilyModel:
    family = ProductFamilyModel(
        code="fire_damper_rectangular",
        name="Fire Damper Rectangular",
        description="Rectangular fire damper for HVAC systems",
        is_active=True,
    )

    add_integer_attribute(
        family,
        code="width",
        name="Width",
        min_int=200,
        max_int=2000,
        is_required=True,
    )
    add_integer_attribute(
        family,
        code="height",
        name="Height",
        min_int=200,
        max_int=1500,
        is_required=True,
    )
    add_enum_attribute(
        family,
        code="fire_class",
        name="Fire Class",
        options=["EI60", "EI120"],
        is_required=True,
    )
    add_enum_attribute(
        family,
        code="actuator_type",
        name="Actuator Type",
        options=["standard", "reinforced"],
        is_required=False,
    )
    add_enum_attribute(
        family,
        code="installation_type",
        name="Installation Type",
        options=["wall", "ceiling"],
        is_required=False,
    )

    family.rules.extend(
        [
            ProductRuleModel(
                name="EI120 requires reinforced actuator",
                rule_type=RuleType.REQUIRES_ATTRIBUTE,
                if_attribute_code="fire_class",
                operator=RuleOperator.EQ,
                expected_value="EI120",
                target_attribute_code="actuator_type",
                error_message="Actuator type is required when fire class is EI120.",
                is_active=True,
            ),
            ProductRuleModel(
                name="Wall installation restricts actuator choice",
                rule_type=RuleType.RESTRICTS_VALUE,
                if_attribute_code="installation_type",
                operator=RuleOperator.EQ,
                expected_value="wall",
                target_attribute_code="actuator_type",
                allowed_values=["standard", "reinforced"],
                error_message="Only supported actuator types are allowed for wall installation.",
                is_active=True,
            ),
        ]
    )

    family.pricing_rules.extend(
        [
            ProductPricingRuleModel(
                name="Base price rectangular",
                pricing_rule_type=PricingRuleType.BASE_PRICE,
                amount=500,
                currency="PLN",
                label="Base price",
                is_active=True,
            ),
            ProductPricingRuleModel(
                name="EI120 surcharge rectangular",
                pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
                if_attribute_code="fire_class",
                operator=RuleOperator.EQ,
                expected_value="EI120",
                amount=200,
                currency="PLN",
                label="EI120 surcharge",
                is_active=True,
            ),
            ProductPricingRuleModel(
                name="Large width surcharge rectangular",
                pricing_rule_type=PricingRuleType.PERCENTAGE_SURCHARGE,
                if_attribute_code="width",
                operator=RuleOperator.GT,
                expected_value="1200",
                amount=15,
                currency="PLN",
                label="Large width surcharge",
                is_active=True,
            ),
        ]
    )

    return family


def seed_round_fire_damper() -> ProductFamilyModel:
    family = ProductFamilyModel(
        code="fire_damper_round",
        name="Fire Damper Round",
        description="Round fire damper for circular duct systems",
        is_active=True,
    )

    add_integer_attribute(
        family,
        code="diameter",
        name="Diameter",
        min_int=100,
        max_int=1000,
        is_required=True,
    )
    add_enum_attribute(
        family,
        code="fire_class",
        name="Fire Class",
        options=["EI60", "EI120"],
        is_required=True,
    )
    add_enum_attribute(
        family,
        code="actuator_type",
        name="Actuator Type",
        options=["standard", "reinforced"],
        is_required=False,
    )
    add_enum_attribute(
        family,
        code="installation_type",
        name="Installation Type",
        options=["wall", "ceiling"],
        is_required=False,
    )

    family.rules.extend(
        [
            ProductRuleModel(
                name="EI120 requires actuator round",
                rule_type=RuleType.REQUIRES_ATTRIBUTE,
                if_attribute_code="fire_class",
                operator=RuleOperator.EQ,
                expected_value="EI120",
                target_attribute_code="actuator_type",
                error_message="Actuator type is required when fire class is EI120.",
                is_active=True,
            ),
        ]
    )

    family.pricing_rules.extend(
        [
            ProductPricingRuleModel(
                name="Base price round",
                pricing_rule_type=PricingRuleType.BASE_PRICE,
                amount=450,
                currency="PLN",
                label="Base price",
                is_active=True,
            ),
            ProductPricingRuleModel(
                name="EI120 surcharge round",
                pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
                if_attribute_code="fire_class",
                operator=RuleOperator.EQ,
                expected_value="EI120",
                amount=180,
                currency="PLN",
                label="EI120 surcharge",
                is_active=True,
            ),
            ProductPricingRuleModel(
                name="Large diameter surcharge round",
                pricing_rule_type=PricingRuleType.PERCENTAGE_SURCHARGE,
                if_attribute_code="diameter",
                operator=RuleOperator.GT,
                expected_value="600",
                amount=10,
                currency="PLN",
                label="Large diameter surcharge",
                is_active=True,
            ),
        ]
    )

    return family


def seed_multi_blade_fire_damper() -> ProductFamilyModel:
    family = ProductFamilyModel(
        code="multi_blade_fire_damper",
        name="Multi Blade Fire Damper",
        description="Multi-blade fire damper for larger ventilation openings",
        is_active=True,
    )

    add_integer_attribute(
        family,
        code="width",
        name="Width",
        min_int=300,
        max_int=2500,
        is_required=True,
    )
    add_integer_attribute(
        family,
        code="height",
        name="Height",
        min_int=300,
        max_int=2000,
        is_required=True,
    )
    add_enum_attribute(
        family,
        code="fire_class",
        name="Fire Class",
        options=["EI60", "EI120"],
        is_required=True,
    )
    add_enum_attribute(
        family,
        code="blade_type",
        name="Blade Type",
        options=["standard", "insulated"],
        is_required=True,
    )
    add_enum_attribute(
        family,
        code="installation_type",
        name="Installation Type",
        options=["wall", "ceiling"],
        is_required=False,
    )

    family.rules.extend(
        [
            ProductRuleModel(
                name="EI120 requires insulated blades",
                rule_type=RuleType.RESTRICTS_VALUE,
                if_attribute_code="fire_class",
                operator=RuleOperator.EQ,
                expected_value="EI120",
                target_attribute_code="blade_type",
                allowed_values=["insulated"],
                error_message="EI120 requires insulated blades.",
                is_active=True,
            ),
        ]
    )

    family.pricing_rules.extend(
        [
            ProductPricingRuleModel(
                name="Base price multi blade",
                pricing_rule_type=PricingRuleType.BASE_PRICE,
                amount=700,
                currency="PLN",
                label="Base price",
                is_active=True,
            ),
            ProductPricingRuleModel(
                name="EI120 surcharge multi blade",
                pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
                if_attribute_code="fire_class",
                operator=RuleOperator.EQ,
                expected_value="EI120",
                amount=250,
                currency="PLN",
                label="EI120 surcharge",
                is_active=True,
            ),
            ProductPricingRuleModel(
                name="Insulated blade surcharge",
                pricing_rule_type=PricingRuleType.FIXED_SURCHARGE,
                if_attribute_code="blade_type",
                operator=RuleOperator.EQ,
                expected_value="insulated",
                amount=120,
                currency="PLN",
                label="Insulated blade surcharge",
                is_active=True,
            ),
        ]
    )

    return family


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

        for family in families_to_seed:
            if family.code in existing_codes:
                print(f"Skipping existing family: {family.code}")
                continue

            session.add(family)
            print(f"Seeded family: {family.code}")

        session.commit()
        print("Demo seed completed.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()