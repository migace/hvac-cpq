from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QuoteStatusEnum(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProductQuoteCreate(BaseModel):
    product_configuration_id: int


class ProductQuoteRead(BaseModel):
    id: int
    product_configuration_id: int
    quote_number: str
    status: QuoteStatusEnum
    currency: str
    base_price: Decimal
    surcharge_total: Decimal
    total_price: Decimal
    configuration_snapshot: dict[str, Any]
    pricing_snapshot: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}