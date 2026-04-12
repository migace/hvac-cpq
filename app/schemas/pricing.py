from decimal import Decimal

from pydantic import BaseModel

from app.schemas.product_configuration import ProductConfigurationCreate


class PriceBreakdownItemRead(BaseModel):
    rule_name: str
    label: str
    amount: Decimal


class PricingResponse(BaseModel):
    currency: str
    base_price: Decimal
    surcharge_total: Decimal
    total_price: Decimal
    breakdown: list[PriceBreakdownItemRead]