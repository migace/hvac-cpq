from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from app.schemas.product_rule import RuleOperatorEnum


class PricingRuleTypeEnum(StrEnum):
    BASE_PRICE = "base_price"
    FIXED_SURCHARGE = "fixed_surcharge"
    PERCENTAGE_SURCHARGE = "percentage_surcharge"


class ProductPricingRuleCreate(BaseModel):
    product_family_id: int
    name: str = Field(min_length=1, max_length=255)
    pricing_rule_type: PricingRuleTypeEnum

    if_attribute_code: str | None = Field(default=None, max_length=100)
    operator: RuleOperatorEnum | None = None
    expected_value: str | None = Field(default=None, max_length=255)

    amount: Decimal = Field(gt=0)
    currency: str = Field(default="PLN", min_length=3, max_length=3)
    label: str = Field(min_length=1, max_length=255)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_rule_shape(self) -> "ProductPricingRuleCreate":
        if self.pricing_rule_type == PricingRuleTypeEnum.BASE_PRICE:
            if self.if_attribute_code or self.operator or self.expected_value:
                raise ValueError("base_price rule cannot define condition fields.")
        else:
            if not self.if_attribute_code or not self.operator or self.expected_value is None:
                raise ValueError(
                    "Conditional pricing rules require "
                    "if_attribute_code, operator and expected_value."
                )

        return self


class ProductPricingRuleRead(BaseModel):
    id: int
    product_family_id: int
    name: str
    pricing_rule_type: PricingRuleTypeEnum
    if_attribute_code: str | None
    operator: RuleOperatorEnum | None
    expected_value: str | None
    amount: Decimal
    currency: str
    label: str
    is_active: bool

    model_config = {"from_attributes": True}