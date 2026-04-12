from enum import Enum

from pydantic import BaseModel, Field, model_validator


class RuleTypeEnum(str, Enum):
    REQUIRES_ATTRIBUTE = "requires_attribute"
    FORBIDS_ATTRIBUTE = "forbids_attribute"
    RESTRICTS_VALUE = "restricts_value"


class RuleOperatorEnum(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"


class ProductRuleCreate(BaseModel):
    product_family_id: int
    name: str = Field(min_length=1, max_length=255)
    rule_type: RuleTypeEnum

    if_attribute_code: str = Field(min_length=1, max_length=100)
    operator: RuleOperatorEnum
    expected_value: str = Field(min_length=1, max_length=255)

    target_attribute_code: str = Field(min_length=1, max_length=100)
    allowed_values: list[str] = Field(default_factory=list)

    error_message: str = Field(min_length=1)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_rule_shape(self) -> "ProductRuleCreate":
        if self.rule_type == RuleTypeEnum.RESTRICTS_VALUE and not self.allowed_values:
            raise ValueError("restricts_value rule requires allowed_values.")

        if self.rule_type != RuleTypeEnum.RESTRICTS_VALUE and self.allowed_values:
            raise ValueError("allowed_values can only be used with restricts_value rules.")

        return self


class ProductRuleRead(BaseModel):
    id: int
    product_family_id: int
    name: str
    rule_type: RuleTypeEnum
    if_attribute_code: str
    operator: RuleOperatorEnum
    expected_value: str
    target_attribute_code: str
    allowed_values: list[str] = Field(default_factory=list)
    error_message: str
    is_active: bool

    model_config = {"from_attributes": True}