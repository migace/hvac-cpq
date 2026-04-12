from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.product_pricing_rule import ProductPricingRuleCreate, ProductPricingRuleRead
from app.services.product_pricing_rule_service import ProductPricingRuleService

router = APIRouter(prefix="/product-pricing-rules", tags=["product-pricing-rules"])


@router.post("", response_model=ProductPricingRuleRead, status_code=status.HTTP_201_CREATED)
def create_product_pricing_rule(
    payload: ProductPricingRuleCreate,
    session: Session = Depends(get_db_session),
) -> ProductPricingRuleRead:
    service = ProductPricingRuleService(session)
    rule = service.create_pricing_rule(payload)
    return ProductPricingRuleRead.model_validate(rule)


@router.get("/family/{family_id}", response_model=list[ProductPricingRuleRead])
def list_product_pricing_rules_for_family(
    family_id: int,
    session: Session = Depends(get_db_session),
) -> list[ProductPricingRuleRead]:
    service = ProductPricingRuleService(session)
    rules = service.list_pricing_rules_for_family(family_id)
    return [ProductPricingRuleRead.model_validate(rule) for rule in rules]