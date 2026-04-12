from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class AttributeTypeEnum(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    ENUM = "enum"


class AttributeOptionCreate(BaseModel):
    value: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=255)
    sort_order: int = 0


class AttributeDefinitionCreate(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    attribute_type: AttributeTypeEnum
    is_required: bool = False
    unit: str | None = Field(default=None, max_length=50)

    min_int: int | None = None
    max_int: int | None = None
    min_decimal: Decimal | None = None
    max_decimal: Decimal | None = None

    enum_options: list[AttributeOptionCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_attribute_constraints(self) -> "AttributeDefinitionCreate":
        if self.attribute_type == AttributeTypeEnum.INTEGER:
            if self.min_decimal is not None or self.max_decimal is not None:
                raise ValueError("Decimal bounds are not allowed for integer attributes.")

        if self.attribute_type == AttributeTypeEnum.DECIMAL:
            if self.min_int is not None or self.max_int is not None:
                raise ValueError("Integer bounds are not allowed for decimal attributes.")

        if self.attribute_type == AttributeTypeEnum.ENUM:
            if not self.enum_options:
                raise ValueError("Enum attributes must define at least one option.")

        if self.attribute_type != AttributeTypeEnum.ENUM and self.enum_options:
            raise ValueError("Only enum attributes can define enum options.")

        if self.min_int is not None and self.max_int is not None and self.min_int > self.max_int:
            raise ValueError("min_int cannot be greater than max_int.")

        if (
                self.min_decimal is not None
                and self.max_decimal is not None
                and self.min_decimal > self.max_decimal
        ):
            raise ValueError("min_decimal cannot be greater than max_decimal.")

        return self


class ProductFamilyCreate(BaseModel):
    code: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_active: bool = True
    attributes: list[AttributeDefinitionCreate] = Field(default_factory=list)


class AttributeOptionRead(BaseModel):
    id: int
    value: str
    label: str
    sort_order: int

    model_config = {"from_attributes": True}


class AttributeDefinitionRead(BaseModel):
    id: int
    code: str
    name: str
    description: str | None
    attribute_type: AttributeTypeEnum
    is_required: bool
    unit: str | None
    min_int: int | None
    max_int: int | None
    min_decimal: Decimal | None
    max_decimal: Decimal | None
    enum_options: list[AttributeOptionRead]

    model_config = {"from_attributes": True}


class ProductFamilyRead(BaseModel):
    id: int
    code: str
    name: str
    description: str | None
    is_active: bool
    attributes: list[AttributeDefinitionRead]

    model_config = {"from_attributes": True}
