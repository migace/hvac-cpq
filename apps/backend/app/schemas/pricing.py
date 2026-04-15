from decimal import Decimal

from pydantic import BaseModel


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