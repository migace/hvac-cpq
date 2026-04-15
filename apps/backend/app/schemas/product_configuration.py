from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, model_validator


class AttributeValueCreate(BaseModel):
    attribute_code: str = Field(min_length=1, max_length=100)
    value: Any


class ProductConfigurationCreate(BaseModel):
    product_family_id: int
    name: str = Field(min_length=1, max_length=255)
    status: str = Field(default="draft", min_length=1, max_length=50)
    values: list[AttributeValueCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def ensure_unique_attribute_codes(self) -> ProductConfigurationCreate:
        codes = [item.attribute_code for item in self.values]
        if len(codes) != len(set(codes)):
            raise ValueError("Duplicate attribute codes are not allowed in a configuration.")
        return self


class AttributeValueRead(BaseModel):
    attribute_code: str
    attribute_name: str
    attribute_type: str
    unit: str | None
    value: str | int | Decimal | bool | None


class ProductConfigurationListItem(BaseModel):
    id: int
    product_family_id: int
    product_family_code: str
    name: str
    status: str
    values_count: int


class ProductConfigurationRead(BaseModel):
    id: int
    product_family_id: int
    name: str
    status: str
    values: list[AttributeValueRead]