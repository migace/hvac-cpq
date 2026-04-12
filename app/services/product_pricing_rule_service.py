from app.core.db_utils import commit_and_refresh
from app.db.models import ProductPricingRuleModel, PricingRuleType, RuleOperator
from app.domain.exceptions import ProductFamilyNotFoundError, ProductRuleDefinitionError
from app.repositories.product_family_repository import ProductFamilyRepository
from app.repositories.product_pricing_rule_repository import ProductPricingRuleRepository
from app.schemas.product_pricing_rule import ProductPricingRuleCreate


class ProductPricingRuleService:
    def __init__(self, session) -> None:
        self.session = session
        self.family_repository = ProductFamilyRepository(session)
        self.pricing_rule_repository = ProductPricingRuleRepository(session)

    def create_pricing_rule(self, payload: ProductPricingRuleCreate) -> ProductPricingRuleModel:
        family = self.family_repository.get_by_id(payload.product_family_id)
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

        self.pricing_rule_repository.add(rule)
        commit_and_refresh(self.session, rule)
        return rule

    def list_pricing_rules_for_family(self, family_id: int) -> list[ProductPricingRuleModel]:
        return self.pricing_rule_repository.list_for_family(family_id)