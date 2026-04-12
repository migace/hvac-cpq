from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    AttributeDefinitionModel,
    AttributeType,
    AttributeValueModel,
    ProductConfigurationModel,
    ProductFamilyModel,
)
from app.domain.exceptions import (
    AttributeDefinitionNotFoundError,
    InvalidAttributeValueError,
    ProductConfigurationNotFoundError,
    ProductFamilyNotFoundError,
)
from app.schemas.product_configuration import ProductConfigurationCreate
from app.services.configuration_validator import ConfigurationValidator
from app.services.rule_engine import RuleEngine
from app.services.pricing_engine import PricingEngine, PricingResult

from app.repositories.product_configuration_repository import ProductConfigurationRepository
from app.repositories.product_family_repository import ProductFamilyRepository


class ProductConfigurationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.validator = ConfigurationValidator()
        self.rule_engine = RuleEngine()
        self.pricing_engine = PricingEngine()
        self.family_repository = ProductFamilyRepository(session)
        self.configuration_repository = ProductConfigurationRepository(session)

    def create_configuration(self, payload: ProductConfigurationCreate) -> ProductConfigurationModel:
        family = self.family_repository.get_by_id(payload.product_family_id)
        if not family:
            raise ProductFamilyNotFoundError(
                f"Product family with id '{payload.product_family_id}' not found."
            )

        attribute_map = {attribute.code: attribute for attribute in family.attributes}
        provided_attribute_codes = {item.attribute_code for item in payload.values}

        self.validator.validate_presence(
            family=family,
            provided_attribute_codes=provided_attribute_codes,
        )

        configuration_values: dict[str, Any] = {}
        value_models: list[AttributeValueModel] = []

        for item in payload.values:
            attribute_definition = attribute_map.get(item.attribute_code)
            if not attribute_definition:
                available_attributes = ", ".join(sorted(attribute_map.keys()))
                raise AttributeDefinitionNotFoundError(
                    f"Attribute '{item.attribute_code}' does not exist in family '{family.code}'. "
                    f"Available attributes: {available_attributes}."
                )

            normalized_value, value_model = self._build_attribute_value(
                attribute_definition,
                item.value,
            )
            configuration_values[item.attribute_code] = normalized_value
            value_models.append(value_model)

        self.rule_engine.evaluate(
            rules=list(family.rules),
            configuration_values=configuration_values,
        )

        configuration = ProductConfigurationModel(
            product_family_id=payload.product_family_id,
            name=payload.name,
            status=payload.status,
        )
        configuration.values.extend(value_models)

        self.configuration_repository.add(configuration)
        self.session.commit()

        return self.configuration_repository.get_by_id(configuration.id)

    def get_configuration(self, configuration_id: int) -> ProductConfigurationModel:
        configuration = self.configuration_repository.get_by_id(configuration_id)
        if not configuration:
            raise ProductConfigurationNotFoundError(
                f"Product configuration with id '{configuration_id}' not found."
            )
        return configuration

    def _build_attribute_value(
            self,
            attribute_definition: AttributeDefinitionModel,
            raw_value: Any,
    ) -> tuple[Any, AttributeValueModel]:
        attribute_type = attribute_definition.attribute_type

        if attribute_type == AttributeType.STRING:
            if not isinstance(raw_value, str):
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' expects a string."
                )
            return raw_value, AttributeValueModel(
                attribute_definition_id=attribute_definition.id,
                value_string=raw_value,
            )

        if attribute_type == AttributeType.ENUM:
            if not isinstance(raw_value, str):
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' expects a string enum value."
                )

            allowed_values = {option.value for option in attribute_definition.enum_options}
            if raw_value not in allowed_values:
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' must be one of: "
                    f"{', '.join(sorted(allowed_values))}."
                )

            return raw_value, AttributeValueModel(
                attribute_definition_id=attribute_definition.id,
                value_string=raw_value,
            )

        if attribute_type == AttributeType.INTEGER:
            if isinstance(raw_value, bool) or not isinstance(raw_value, int):
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' expects an integer."
                )

            if attribute_definition.min_int is not None and raw_value < attribute_definition.min_int:
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' must be >= {attribute_definition.min_int}."
                )

            if attribute_definition.max_int is not None and raw_value > attribute_definition.max_int:
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' must be <= {attribute_definition.max_int}."
                )

            return raw_value, AttributeValueModel(
                attribute_definition_id=attribute_definition.id,
                value_integer=raw_value,
            )

        if attribute_type == AttributeType.DECIMAL:
            if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float, str, Decimal)):
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' expects a decimal value."
                )

            try:
                decimal_value = Decimal(str(raw_value))
            except Exception as exc:
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' expects a valid decimal value."
                ) from exc

            if (
                    attribute_definition.min_decimal is not None
                    and decimal_value < attribute_definition.min_decimal
            ):
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' must be >= "
                    f"{attribute_definition.min_decimal}."
                )

            if (
                    attribute_definition.max_decimal is not None
                    and decimal_value > attribute_definition.max_decimal
            ):
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' must be <= "
                    f"{attribute_definition.max_decimal}."
                )

            return decimal_value, AttributeValueModel(
                attribute_definition_id=attribute_definition.id,
                value_decimal=decimal_value,
            )

        if attribute_type == AttributeType.BOOLEAN:
            if not isinstance(raw_value, bool):
                raise InvalidAttributeValueError(
                    f"Attribute '{attribute_definition.code}' expects a boolean."
                )

            return raw_value, AttributeValueModel(
                attribute_definition_id=attribute_definition.id,
                value_boolean=raw_value,
            )

        raise InvalidAttributeValueError(
            f"Unsupported attribute type for '{attribute_definition.code}'."
        )

    def calculate_configuration_price(self, payload: ProductConfigurationCreate) -> PricingResult:
        family, configuration_values = self.build_configuration_values_map(payload)

        return self.pricing_engine.calculate(
            pricing_rules=list(family.pricing_rules),
            configuration_values=configuration_values,
        )

    def calculate_price_from_stored_values(
        self,
        family: ProductFamilyModel,
        values: list[AttributeValueModel],
    ) -> PricingResult:
        configuration_values = {
            v.attribute_definition.code: v.resolved_value
            for v in values
        }
        return self.pricing_engine.calculate(
            pricing_rules=list(family.pricing_rules),
            configuration_values=configuration_values,
        )

    def build_configuration_values_map(self, payload: ProductConfigurationCreate) -> tuple[ProductFamilyModel, dict[str, Any]]:
        family = self.family_repository.get_by_id(payload.product_family_id)
        if not family:
            raise ProductFamilyNotFoundError(
                f"Product family with id '{payload.product_family_id}' not found."
            )

        attribute_map = {attribute.code: attribute for attribute in family.attributes}
        provided_attribute_codes = {item.attribute_code for item in payload.values}

        self.validator.validate_presence(
            family=family,
            provided_attribute_codes=provided_attribute_codes,
        )

        configuration_values: dict[str, Any] = {}

        for item in payload.values:
            attribute_definition = attribute_map.get(item.attribute_code)
            if not attribute_definition:
                available_attributes = ", ".join(sorted(attribute_map.keys()))
                raise AttributeDefinitionNotFoundError(
                    f"Attribute '{item.attribute_code}' does not exist in family '{family.code}'. "
                    f"Available attributes: {available_attributes}."
                )

            normalized_value, _ = self._build_attribute_value(
                attribute_definition,
                item.value,
            )
            configuration_values[item.attribute_code] = normalized_value

        self.rule_engine.evaluate(
            rules=list(family.rules),
            configuration_values=configuration_values,
        )

        return family, configuration_values
