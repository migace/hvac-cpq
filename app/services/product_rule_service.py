from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    AttributeDefinitionModel,
    ProductFamilyModel,
    ProductRuleModel,
    RuleOperator,
    RuleType,
)
from app.domain.exceptions import ProductFamilyNotFoundError, ProductRuleDefinitionError
from app.schemas.product_rule import ProductRuleCreate


class ProductRuleService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_rule(self, payload: ProductRuleCreate) -> ProductRuleModel:
        family = self.session.scalar(
            select(ProductFamilyModel)
            .options(selectinload(ProductFamilyModel.attributes))
            .where(ProductFamilyModel.id == payload.product_family_id)
        )
        if not family:
            raise ProductFamilyNotFoundError(
                f"Product family with id '{payload.product_family_id}' not found."
            )

        available_codes = {attribute.code for attribute in family.attributes}
        for code in [payload.if_attribute_code, payload.target_attribute_code]:
            if code not in available_codes:
                raise ProductRuleDefinitionError(
                    f"Attribute '{code}' does not exist in family '{family.code}'."
                )

        rule = ProductRuleModel(
            product_family_id=payload.product_family_id,
            name=payload.name,
            rule_type=RuleType(payload.rule_type.value),
            if_attribute_code=payload.if_attribute_code,
            operator=RuleOperator(payload.operator.value),
            expected_value=payload.expected_value,
            target_attribute_code=payload.target_attribute_code,
            allowed_values=",".join(payload.allowed_values) if payload.allowed_values else None,
            error_message=payload.error_message,
            is_active=payload.is_active,
        )

        self.session.add(rule)
        self.session.commit()
        self.session.refresh(rule)
        return rule

    def list_rules_for_family(self, family_id: int) -> list[ProductRuleModel]:
        result = self.session.scalars(
            select(ProductRuleModel)
            .where(ProductRuleModel.product_family_id == family_id)
            .order_by(ProductRuleModel.id.asc())
        )
        return list(result.all())