from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AttributeType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    ENUM = "enum"


class ConfigurationStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ProductFamilyModel(Base):
    __tablename__ = "product_families"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    attributes: Mapped[list["AttributeDefinitionModel"]] = relationship(
        back_populates="product_family",
        cascade="all, delete-orphan",
    )
    configurations: Mapped[list["ProductConfigurationModel"]] = relationship(
        back_populates="product_family",
        cascade="all, delete-orphan",
    )

    rules: Mapped[list["ProductRuleModel"]] = relationship(
        back_populates="product_family",
        cascade="all, delete-orphan",
    )

    pricing_rules: Mapped[list["ProductPricingRuleModel"]] = relationship(
        back_populates="product_family",
        cascade="all, delete-orphan",
    )


class AttributeDefinitionModel(Base):
    __tablename__ = "attribute_definitions"
    __table_args__ = (
        UniqueConstraint("product_family_id", "code", name="uq_attribute_definition_family_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_family_id: Mapped[int] = mapped_column(
        ForeignKey("product_families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    attribute_type: Mapped[AttributeType] = mapped_column(
        SqlEnum(AttributeType, name="attribute_type_enum"),
        nullable=False,
    )

    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    min_int: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_int: Mapped[int | None] = mapped_column(Integer, nullable=True)

    min_decimal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    max_decimal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    product_family: Mapped["ProductFamilyModel"] = relationship(back_populates="attributes")
    enum_options: Mapped[list["AttributeOptionModel"]] = relationship(
        back_populates="attribute_definition",
        cascade="all, delete-orphan",
    )
    values: Mapped[list["AttributeValueModel"]] = relationship(back_populates="attribute_definition")


class AttributeOptionModel(Base):
    __tablename__ = "attribute_options"
    __table_args__ = (
        UniqueConstraint("attribute_definition_id", "value", name="uq_attribute_option_value"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    attribute_definition_id: Mapped[int] = mapped_column(
        ForeignKey("attribute_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    value: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    attribute_definition: Mapped["AttributeDefinitionModel"] = relationship(
        back_populates="enum_options"
    )


class ProductConfigurationModel(Base):
    __tablename__ = "product_configurations"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_family_id: Mapped[int] = mapped_column(
        ForeignKey("product_families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ConfigurationStatus] = mapped_column(
        SqlEnum(ConfigurationStatus, name="configuration_status_enum"),
        default=ConfigurationStatus.DRAFT,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    product_family: Mapped["ProductFamilyModel"] = relationship(back_populates="configurations")
    values: Mapped[list["AttributeValueModel"]] = relationship(
        back_populates="configuration",
        cascade="all, delete-orphan",
    )
    quotes: Mapped[list["ProductQuoteModel"]] = relationship(
        back_populates="configuration",
        cascade="all, delete-orphan",
    )


class AttributeValueModel(Base):
    __tablename__ = "attribute_values"
    __table_args__ = (
        UniqueConstraint(
            "configuration_id",
            "attribute_definition_id",
            name="uq_attribute_value_configuration_attribute",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    configuration_id: Mapped[int] = mapped_column(
        ForeignKey("product_configurations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attribute_definition_id: Mapped[int] = mapped_column(
        ForeignKey("attribute_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    value_string: Mapped[str | None] = mapped_column(String(255), nullable=True)
    value_integer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    value_decimal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    value_boolean: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    configuration: Mapped["ProductConfigurationModel"] = relationship(back_populates="values")
    attribute_definition: Mapped["AttributeDefinitionModel"] = relationship(back_populates="values")

    @property
    def resolved_value(self) -> Any:
        if self.value_integer is not None:
            return self.value_integer
        if self.value_decimal is not None:
            return self.value_decimal
        if self.value_boolean is not None:
            return self.value_boolean
        return self.value_string


class RuleType(str, Enum):
    REQUIRES_ATTRIBUTE = "requires_attribute"
    FORBIDS_ATTRIBUTE = "forbids_attribute"
    RESTRICTS_VALUE = "restricts_value"


class RuleOperator(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"


class ProductRuleModel(Base):
    __tablename__ = "product_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_family_id: Mapped[int] = mapped_column(
        ForeignKey("product_families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_type: Mapped[RuleType] = mapped_column(
        SqlEnum(RuleType, name="rule_type_enum"),
        nullable=False,
    )

    if_attribute_code: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[RuleOperator] = mapped_column(
        SqlEnum(RuleOperator, name="rule_operator_enum"),
        nullable=False,
    )
    expected_value: Mapped[str] = mapped_column(String(255), nullable=False)

    target_attribute_code: Mapped[str] = mapped_column(String(100), nullable=False)

    allowed_values: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        comment="List of allowed values used by restricts_value rules.",
    )

    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    product_family: Mapped["ProductFamilyModel"] = relationship(back_populates="rules")


class PricingRuleType(str, Enum):
    BASE_PRICE = "base_price"
    FIXED_SURCHARGE = "fixed_surcharge"
    PERCENTAGE_SURCHARGE = "percentage_surcharge"


class ProductPricingRuleModel(Base):
    __tablename__ = "product_pricing_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_family_id: Mapped[int] = mapped_column(
        ForeignKey("product_families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    pricing_rule_type: Mapped[PricingRuleType] = mapped_column(
        SqlEnum(PricingRuleType, name="pricing_rule_type_enum"),
        nullable=False,
    )

    if_attribute_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    operator: Mapped[RuleOperator | None] = mapped_column(
        SqlEnum(RuleOperator, name="rule_operator_enum", create_type=False),
        nullable=True,
    )
    expected_value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    currency: Mapped[str] = mapped_column(String(3), default="PLN", nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    product_family: Mapped["ProductFamilyModel"] = relationship(back_populates="pricing_rules")


class QuoteStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProductQuoteModel(Base):
    __tablename__ = "product_quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_configuration_id: Mapped[int] = mapped_column(
        ForeignKey("product_configurations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    quote_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    status: Mapped[QuoteStatus] = mapped_column(
        SqlEnum(QuoteStatus, name="quote_status_enum"),
        nullable=False,
        default=QuoteStatus.GENERATED,
    )

    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    surcharge_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    configuration_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    pricing_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    configuration: Mapped["ProductConfigurationModel"] = relationship(back_populates="quotes")