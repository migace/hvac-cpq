from decimal import Decimal

from pydantic import BaseModel


class TechnicalCalculationItem(BaseModel):
    name: str
    code: str
    value: Decimal
    unit: str


class TechnicalCalculationResponse(BaseModel):
    family_code: str
    results: list[TechnicalCalculationItem]