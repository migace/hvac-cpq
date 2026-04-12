from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.product_configuration_service import ProductConfigurationService
from app.services.product_family_service import ProductFamilyService
from app.services.product_pricing_rule_service import ProductPricingRuleService
from app.services.product_quote_service import ProductQuoteService
from app.services.product_rule_service import ProductRuleService


def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_product_family_service(
    session: Session = Depends(get_db_session),
) -> ProductFamilyService:
    return ProductFamilyService(session)


def get_product_configuration_service(
    session: Session = Depends(get_db_session),
) -> ProductConfigurationService:
    return ProductConfigurationService(session)


def get_product_rule_service(
    session: Session = Depends(get_db_session),
) -> ProductRuleService:
    return ProductRuleService(session)


def get_product_pricing_rule_service(
    session: Session = Depends(get_db_session),
) -> ProductPricingRuleService:
    return ProductPricingRuleService(session)


def get_product_quote_service(
    session: Session = Depends(get_db_session),
) -> ProductQuoteService:
    return ProductQuoteService(session)