from app.core.db_utils import commit_and_refresh
from app.db.models import ProductRuleModel, RuleOperator, RuleType
from app.domain.exceptions import ProductFamilyNotFoundError, ProductRuleDefinitionError
from app.repositories.product_family_repository import ProductFamilyRepository
from app.repositories.product_rule_repository import ProductRuleRepository
from app.schemas.product_rule import ProductRuleCreate


class ProductRuleService:
    def __init__(self, session) -> None:
        self.session = session
        self.family_repository = ProductFamilyRepository(session)
        self.rule_repository = ProductRuleRepository(session)

    def create_rule(self, payload: ProductRuleCreate) -> ProductRuleModel:
        family = self.family_repository.get_by_id(payload.product_family_id)
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
            allowed_values=payload.allowed_values if payload.allowed_values else None,
            error_message=payload.error_message,
            is_active=payload.is_active,
        )

        self.rule_repository.add(rule)
        commit_and_refresh(self.session, rule)
        return rule

    def list_rules_for_family(self, family_id: int) -> list[ProductRuleModel]:
        return self.rule_repository.list_for_family(family_id)