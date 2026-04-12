from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    AttributeDefinitionModel,
    AttributeValueModel,
    ProductConfigurationModel,
    ProductFamilyModel,
    ProductQuoteModel,
    QuoteStatus,
)
from app.domain.exceptions import ProductConfigurationNotFoundError, ProductQuoteNotFoundError
from app.schemas.product_configuration import ProductConfigurationCreate
from app.services.product_configuration_service import ProductConfigurationService
from app.services.quote_number_service import QuoteNumberService


class ProductQuoteService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.configuration_service = ProductConfigurationService(session)
        self.quote_number_service = QuoteNumberService()

    def create_quote(self, configuration_id: int) -> ProductQuoteModel:
        configuration = self.session.scalar(
            select(ProductConfigurationModel)
            .options(
                selectinload(ProductConfigurationModel.product_family).selectinload(
                    ProductFamilyModel.attributes
                ),
                selectinload(ProductConfigurationModel.values).selectinload(
                    AttributeValueModel.attribute_definition
                ),
            )
            .where(ProductConfigurationModel.id == configuration_id)
        )
        if not configuration:
            raise ProductConfigurationNotFoundError(
                f"Product configuration with id '{configuration_id}' not found."
            )

        payload = ProductConfigurationCreate(
            product_family_id=configuration.product_family_id,
            name=configuration.name,
            status=configuration.status,
            values=[
                {
                    "attribute_code": value.attribute_definition.code,
                    "value": self._extract_value(value),
                }
                for value in configuration.values
            ],
        )

        pricing_result = self.configuration_service.calculate_configuration_price(payload)

        quote = ProductQuoteModel(
            product_configuration_id=configuration.id,
            quote_number=self.quote_number_service.generate(),
            status=QuoteStatus.GENERATED,
            currency=pricing_result.currency,
            base_price=pricing_result.base_price,
            surcharge_total=pricing_result.surcharge_total,
            total_price=pricing_result.total_price,
            configuration_snapshot=self._build_configuration_snapshot(configuration),
            pricing_snapshot=self._build_pricing_snapshot(pricing_result),
        )

        self.session.add(quote)
        self.session.commit()
        self.session.refresh(quote)
        return quote

    def get_quote(self, quote_id: int) -> ProductQuoteModel:
        quote = self.session.scalar(
            select(ProductQuoteModel).where(ProductQuoteModel.id == quote_id)
        )
        if not quote:
            raise ProductQuoteNotFoundError(f"Quote with id '{quote_id}' not found.")
        return quote

    def list_quotes(self) -> list[ProductQuoteModel]:
        result = self.session.scalars(
            select(ProductQuoteModel).order_by(ProductQuoteModel.id.desc())
        )
        return list(result.all())

    def _extract_value(self, value_obj: AttributeValueModel) -> Any:
        if value_obj.value_integer is not None:
            return value_obj.value_integer
        if value_obj.value_decimal is not None:
            return value_obj.value_decimal
        if value_obj.value_boolean is not None:
            return value_obj.value_boolean
        return value_obj.value_string

    def _build_configuration_snapshot(self, configuration: ProductConfigurationModel) -> dict[str, Any]:
        family = configuration.product_family
        return {
            "product_family_id": family.id,
            "product_family_code": family.code,
            "product_family_name": family.name,
            "configuration_id": configuration.id,
            "configuration_name": configuration.name,
            "status": configuration.status,
            "values": [
                {
                    "attribute_code": value.attribute_definition.code,
                    "attribute_name": value.attribute_definition.name,
                    "attribute_type": value.attribute_definition.attribute_type.value,
                    "unit": value.attribute_definition.unit,
                    "value": self._serialize_value(self._extract_value(value)),
                }
                for value in configuration.values
            ],
        }

    def _build_pricing_snapshot(self, pricing_result) -> dict[str, Any]:
        return {
            "currency": pricing_result.currency,
            "base_price": str(pricing_result.base_price),
            "surcharge_total": str(pricing_result.surcharge_total),
            "total_price": str(pricing_result.total_price),
            "breakdown": [
                {
                    "rule_name": item.rule_name,
                    "label": item.label,
                    "amount": str(item.amount),
                }
                for item in pricing_result.breakdown
            ],
        }

    def _serialize_value(self, value: Any) -> Any:
        if isinstance(value, Decimal):
            return str(value)
        return value