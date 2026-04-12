from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.db.models import ProductPricingRuleModel, PricingRuleType, RuleOperator
from app.domain.exceptions import RuleEvaluationError


@dataclass
class PriceBreakdownItem:
    rule_name: str
    label: str
    amount: Decimal


@dataclass
class PricingResult:
    currency: str
    base_price: Decimal
    surcharge_total: Decimal
    total_price: Decimal
    breakdown: list[PriceBreakdownItem]


class PricingEngine:
    def calculate(
        self,
        pricing_rules: list[ProductPricingRuleModel],
        configuration_values: dict[str, Any],
    ) -> PricingResult:
        active_rules = [rule for rule in pricing_rules if rule.is_active]

        base_rules = [rule for rule in active_rules if rule.pricing_rule_type == PricingRuleType.BASE_PRICE]
        if len(base_rules) != 1:
            raise RuleEvaluationError("Exactly one active base_price rule is required.")

        base_rule = base_rules[0]
        base_price = Decimal(base_rule.amount)
        breakdown = [
            PriceBreakdownItem(
                rule_name=base_rule.name,
                label=base_rule.label,
                amount=base_price,
            )
        ]

        surcharge_total = Decimal("0.00")

        for rule in active_rules:
            if rule.pricing_rule_type == PricingRuleType.BASE_PRICE:
                continue

            if not self._condition_matches(
                actual_value=configuration_values.get(rule.if_attribute_code),
                operator=rule.operator,
                expected_value=rule.expected_value,
            ):
                continue

            if rule.pricing_rule_type == PricingRuleType.FIXED_SURCHARGE:
                surcharge_amount = Decimal(rule.amount)
            elif rule.pricing_rule_type == PricingRuleType.PERCENTAGE_SURCHARGE:
                surcharge_amount = (base_price * Decimal(rule.amount) / Decimal("100")).quantize(Decimal("0.01"))
            else:
                raise RuleEvaluationError(f"Unsupported pricing rule type: {rule.pricing_rule_type}")

            surcharge_total += surcharge_amount
            breakdown.append(
                PriceBreakdownItem(
                    rule_name=rule.name,
                    label=rule.label,
                    amount=surcharge_amount,
                )
            )

        total_price = base_price + surcharge_total
        currency = base_rule.currency

        return PricingResult(
            currency=currency,
            base_price=base_price,
            surcharge_total=surcharge_total,
            total_price=total_price,
            breakdown=breakdown,
        )

    def _condition_matches(
        self,
        actual_value: Any,
        operator: RuleOperator | None,
        expected_value: str | None,
    ) -> bool:
        if operator is None:
            return True
        if actual_value is None or expected_value is None:
            return False

        if operator == RuleOperator.EQ:
            return str(actual_value) == expected_value
        if operator == RuleOperator.NEQ:
            return str(actual_value) != expected_value

        actual_decimal = Decimal(str(actual_value))
        expected_decimal_decimal = Decimal(str(expected_value))

        if operator == RuleOperator.GT:
            return actual_decimal > expected_decimal_decimal
        if operator == RuleOperator.GTE:
            return actual_decimal >= expected_decimal_decimal
        if operator == RuleOperator.LT:
            return actual_decimal < expected_decimal_decimal
        if operator == RuleOperator.LTE:
            return actual_decimal <= expected_decimal_decimal

        if operator == RuleOperator.IN:
            allowed = {item.strip() for item in expected_value.split(",") if item.strip()}
            return str(actual_value) in allowed

        raise RuleEvaluationError(f"Unsupported pricing operator: {operator}")