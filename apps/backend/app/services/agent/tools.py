"""Agent tools — thin wrappers that expose existing services to the LLM via tool calling.

Each tool function:
- receives structured input (already parsed by OpenAI tool calling),
- delegates to existing domain services,
- returns a JSON-serializable dict the LLM can reason about.

No business logic lives here — tools are pure adapters.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import ProductFamilyModel
from app.repositories.product_family_repository import ProductFamilyRepository
from app.services.pricing_engine import PricingEngine
from app.services.order_code_service import OrderCodeService
from app.services.technical_calculation_service import TechnicalCalculationService
from app.services.configuration_validator import ConfigurationValidator
from app.services.rule_engine import RuleEngine


def _decimal_to_str(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    return value


def _serialize_family(family: ProductFamilyModel, *, include_rules: bool = False) -> dict:
    data: dict[str, Any] = {
        "id": family.id,
        "code": family.code,
        "name": family.name,
        "description": family.description,
        "is_active": family.is_active,
        "attributes": [
            {
                "code": attr.code,
                "name": attr.name,
                "type": attr.attribute_type.value,
                "is_required": attr.is_required,
                "unit": attr.unit,
                "min": attr.min_int if attr.min_int is not None else _decimal_to_str(attr.min_decimal),
                "max": attr.max_int if attr.max_int is not None else _decimal_to_str(attr.max_decimal),
                "options": [
                    {"value": opt.value, "label": opt.label}
                    for opt in sorted(attr.enum_options, key=lambda o: o.sort_order)
                ]
                if attr.enum_options
                else None,
            }
            for attr in family.attributes
        ],
    }

    if include_rules:
        data["business_rules"] = [
            {
                "name": rule.name,
                "description": rule.error_message,
                "type": rule.rule_type.value,
                "condition": f"{rule.if_attribute_code} {rule.operator.value} {rule.expected_value}",
                "target": rule.target_attribute_code,
            }
            for rule in family.rules
            if rule.is_active
        ]
        data["pricing_rules"] = [
            {
                "name": rule.name,
                "type": rule.pricing_rule_type.value,
                "amount": _decimal_to_str(rule.amount),
                "currency": rule.currency,
                "label": rule.label,
                "condition": (
                    f"{rule.if_attribute_code} {rule.operator.value} {rule.expected_value}"
                    if rule.if_attribute_code
                    else None
                ),
            }
            for rule in family.pricing_rules
            if rule.is_active
        ]

    return data


class AgentTools:
    """Registry of tools available to the AI agent.

    Each public method is a tool. The class holds a DB session
    so tools can query the database through existing repositories/services.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self.family_repository = ProductFamilyRepository(session)
        self.pricing_engine = PricingEngine()
        self.order_code_service = OrderCodeService()
        self.technical_service = TechnicalCalculationService()
        self.validator = ConfigurationValidator()
        self.rule_engine = RuleEngine()

    def search_products(
        self,
        *,
        query: str | None = None,
        fire_class: str | None = None,
        shape: str | None = None,
    ) -> dict:
        """Search available product families by criteria."""
        families = self.family_repository.list_all()
        results = []

        for family in families:
            if not family.is_active:
                continue

            if shape:
                shape_lower = shape.lower()
                if shape_lower in ("rectangular", "prostokątna", "prostokątny"):
                    if "rectangular" not in family.code:
                        continue
                elif shape_lower in ("round", "okrągła", "okrągły"):
                    if "round" not in family.code:
                        continue
                elif shape_lower in ("multi_blade", "multi-blade", "wielopłaszczyznowa"):
                    if "multi_blade" not in family.code:
                        continue

            if fire_class:
                has_class = False
                for attr in family.attributes:
                    if attr.code == "fire_class":
                        for opt in attr.enum_options:
                            if opt.value.upper() == fire_class.upper():
                                has_class = True
                                break
                if not has_class:
                    continue

            if query:
                query_lower = query.lower()
                searchable = f"{family.name} {family.description or ''} {family.code}".lower()
                if query_lower not in searchable:
                    continue

            results.append(_serialize_family(family))

        return {
            "total": len(results),
            "families": results,
        }

    def get_family_details(self, *, family_id: int) -> dict:
        """Get full details of a product family including rules and pricing."""
        family = self.family_repository.get_by_id(family_id)
        if not family:
            return {"error": f"Product family with id {family_id} not found."}
        return _serialize_family(family, include_rules=True)

    def calculate_price(
        self,
        *,
        family_id: int,
        configuration: dict[str, Any],
    ) -> dict:
        """Calculate price for a given configuration."""
        family = self.family_repository.get_by_id(family_id)
        if not family:
            return {"error": f"Product family with id {family_id} not found."}

        try:
            self._validate_configuration(family, configuration)

            result = self.pricing_engine.calculate(
                pricing_rules=list(family.pricing_rules),
                configuration_values=configuration,
            )
            return {
                "currency": result.currency,
                "base_price": _decimal_to_str(result.base_price),
                "surcharge_total": _decimal_to_str(result.surcharge_total),
                "total_price": _decimal_to_str(result.total_price),
                "breakdown": [
                    {
                        "rule_name": item.rule_name,
                        "label": item.label,
                        "amount": _decimal_to_str(item.amount),
                    }
                    for item in result.breakdown
                ],
            }
        except Exception as exc:
            return {"error": str(exc)}

    def validate_configuration(
        self,
        *,
        family_id: int,
        configuration: dict[str, Any],
    ) -> dict:
        """Validate a configuration against business rules."""
        family = self.family_repository.get_by_id(family_id)
        if not family:
            return {"error": f"Product family with id {family_id} not found."}

        try:
            self._validate_configuration(family, configuration)
            return {"valid": True, "message": "Configuration is valid."}
        except Exception as exc:
            return {"valid": False, "message": str(exc)}

    def generate_order_code(
        self,
        *,
        family_id: int,
        configuration: dict[str, Any],
    ) -> dict:
        """Generate an order code for a valid configuration."""
        family = self.family_repository.get_by_id(family_id)
        if not family:
            return {"error": f"Product family with id {family_id} not found."}

        try:
            order_code = self.order_code_service.generate(
                family_code=family.code,
                configuration_values=configuration,
            )
            return {"order_code": order_code}
        except Exception as exc:
            return {"error": str(exc)}

    def calculate_technical_params(
        self,
        *,
        family_id: int,
        configuration: dict[str, Any],
    ) -> dict:
        """Calculate technical parameters for a configuration."""
        family = self.family_repository.get_by_id(family_id)
        if not family:
            return {"error": f"Product family with id {family_id} not found."}

        try:
            results = self.technical_service.calculate(
                family_code=family.code,
                configuration_values=configuration,
            )
            return {
                "results": [
                    {
                        "name": item.name,
                        "code": item.code,
                        "value": _decimal_to_str(item.value),
                        "unit": item.unit,
                    }
                    for item in results
                ]
            }
        except Exception as exc:
            return {"error": str(exc)}

    def _validate_configuration(
        self,
        family: ProductFamilyModel,
        configuration: dict[str, Any],
    ) -> None:
        provided_codes = set(configuration.keys())
        self.validator.validate_presence(
            family=family,
            provided_attribute_codes=provided_codes,
        )
        self.rule_engine.evaluate(
            rules=list(family.rules),
            configuration_values=configuration,
        )
