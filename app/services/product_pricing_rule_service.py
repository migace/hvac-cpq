from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    ProductFamilyModel,
    ProductPricingRuleModel,
    PricingRuleType,
    RuleOperator,
)
from app.domain.exceptions import ProductFamilyNotFoundError, ProductRuleDefinitionError
from app.schemas.product_pricing_rule import ProductPricingRuleCreate


class ProductPricingRuleService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_pricing_rule(self, payload: ProductPricingRuleCreate) -> ProductPricingRuleModel:
        family = self.session.scalar(
            select(ProductFamilyModel)
            .options(selectinload(ProductFamilyModel.attributes))
            .where(ProductFamilyModel.id == payload.product_family_id)
        )
        if not family:
            raise ProductFamilyNotFoundError(
                f"Product family with id '{payload.product_family_id}' not found."
            )

        if payload.pricing_rule_type != payload.pricing_rule_type.BASE_PRICE:
            available_codes = {attribute.code for attribute in family.attributes}
            if payload.if_attribute_code not in available_codes:
                raise ProductRuleDefinitionError(
                    f"Attribute '{payload.if_attribute_code}' does not exist in family '{family.code}'."
                )

        rule = ProductPricingRuleModel(
            product_family_id=payload.product_family_id,
            name=payload.name,
            pricing_rule_type=PricingRuleType(payload.pricing_rule_type.value),
            if_attribute_code=payload.if_attribute_code,
            operator=RuleOperator(payload.operator.value) if payload.operator else None,
            expected_value=payload.expected_value,
            amount=payload.amount,
            currency=payload.currency,
            label=payload.label,
            is_active=payload.is_active,
        )

        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)
        return rule

    def list_pricing_rules_for_family(self, family_id: int) -> list[ProductPricingRuleModel]:
        result = self.session.scalars(
            select(ProductPricingRuleModel)
            .where(ProductPricingRuleModel.product_family_id == family_id)
            .order_by(ProductPricingRuleModel.id.asc())
        )
        return list(result.all())