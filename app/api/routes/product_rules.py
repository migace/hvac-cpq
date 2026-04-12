from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.product_rule import ProductRuleCreate, ProductRuleRead
from app.services.product_rule_service import ProductRuleService

router = APIRouter(prefix="/product-rules", tags=["product-rules"])


def _to_read_model(rule) -> ProductRuleRead:
    return ProductRuleRead(
        id=rule.id,
        product_family_id=rule.product_family_id,
        name=rule.name,
        rule_type=rule.rule_type.value,
        if_attribute_code=rule.if_attribute_code,
        operator=rule.operator.value,
        expected_value=rule.expected_value,
        target_attribute_code=rule.target_attribute_code,
        allowed_values=rule.allowed_values.split(",") if rule.allowed_values else [],
        error_message=rule.error_message,
        is_active=rule.is_active,
    )


@router.post("", response_model=ProductRuleRead, status_code=status.HTTP_201_CREATED)
def create_product_rule(
    payload: ProductRuleCreate,
    session: Session = Depends(get_db_session),
) -> ProductRuleRead:
    service = ProductRuleService(session)
    rule = service.create_rule(payload)
    return _to_read_model(rule)


@router.get("/family/{family_id}", response_model=list[ProductRuleRead])
def list_product_rules_for_family(
    family_id: int,
    session: Session = Depends(get_db_session),
) -> list[ProductRuleRead]:
    service = ProductRuleService(session)
    rules = service.list_rules_for_family(family_id)
    return [_to_read_model(rule) for rule in rules]