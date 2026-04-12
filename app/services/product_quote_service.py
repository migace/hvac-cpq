from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    ProductConfigurationModel,
    ProductQuoteModel,
    QuoteStatus,
)
from app.domain.exceptions import ProductConfigurationNotFoundError, ProductQuoteNotFoundError
from app.services.pricing_engine import PricingResult
from app.services.product_configuration_service import ProductConfigurationService
from app.services.quote_number_service import QuoteNumberService

from app.core.db_utils import commit_and_refresh
from app.repositories.product_configuration_repository import ProductConfigurationRepository
from app.repositories.product_quote_repository import ProductQuoteRepository


class ProductQuoteService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.configuration_service = ProductConfigurationService(session)
        self.quote_number_service = QuoteNumberService(session)
        self.configuration_repository = ProductConfigurationRepository(session)
        self.quote_repository = ProductQuoteRepository(session)

    def create_quote(self, configuration_id: int) -> ProductQuoteModel:
        configuration = self.configuration_repository.get_by_id(configuration_id)
        if not configuration:
            raise ProductConfigurationNotFoundError(
                f"Product configuration with id '{configuration_id}' not found."
            )

        pricing_result = self.configuration_service.calculate_price_from_stored_values(
            family=configuration.product_family,
            values=list(configuration.values),
        )

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

        self.quote_repository.add(quote)
        commit_and_refresh(self.session, quote)
        return quote

    def get_quote(self, quote_id: int) -> ProductQuoteModel:
        quote = self.quote_repository.get_by_id(quote_id)
        if not quote:
            raise ProductQuoteNotFoundError(f"Quote with id '{quote_id}' not found.")
        return quote

    def list_quotes(self) -> list[ProductQuoteModel]:
        return self.quote_repository.list_all()

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
                    "value": self._serialize_value(value.resolved_value),
                }
                for value in configuration.values
            ],
        }

    def _build_pricing_snapshot(self, pricing_result: PricingResult) -> dict[str, Any]:
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
