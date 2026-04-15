from decimal import Decimal, InvalidOperation
from typing import Any

from app.db.models import ProductRuleModel, RuleOperator, RuleType
from app.domain.exceptions import RuleViolationError


class RuleEngine:
    def evaluate(
        self,
        rules: list[ProductRuleModel],
        configuration_values: dict[str, Any],
    ) -> None:
        for rule in rules:
            if not rule.is_active:
                continue

            if not self._condition_matches(
                actual_value=configuration_values.get(rule.if_attribute_code),
                operator=rule.operator,
                expected_value=rule.expected_value,
            ):
                continue

            self._apply_rule(rule, configuration_values)

    def _condition_matches(
        self,
        actual_value: Any,
        operator: RuleOperator,
        expected_value: str,
    ) -> bool:
        if actual_value is None:
            return False

        if operator == RuleOperator.EQ:
            return str(actual_value) == expected_value

        if operator == RuleOperator.NEQ:
            return str(actual_value) != expected_value

        if operator in {RuleOperator.GT, RuleOperator.GTE, RuleOperator.LT, RuleOperator.LTE}:
            try:
                actual_decimal = Decimal(str(actual_value))
                expected_decimal = Decimal(expected_value)
            except InvalidOperation:
                return False

            if operator == RuleOperator.GT:
                return actual_decimal > expected_decimal
            if operator == RuleOperator.GTE:
                return actual_decimal >= expected_decimal
            if operator == RuleOperator.LT:
                return actual_decimal < expected_decimal
            if operator == RuleOperator.LTE:
                return actual_decimal <= expected_decimal

        if operator == RuleOperator.IN:
            allowed = {item.strip() for item in expected_value.split(",") if item.strip()}
            return str(actual_value) in allowed

        return False

    def _apply_rule(
        self,
        rule: ProductRuleModel,
        configuration_values: dict[str, Any],
    ) -> None:
        target_value = configuration_values.get(rule.target_attribute_code)

        if rule.rule_type == RuleType.REQUIRES_ATTRIBUTE:
            if target_value is None:
                raise RuleViolationError(rule.error_message)
            return

        if rule.rule_type == RuleType.FORBIDS_ATTRIBUTE:
            # For booleans, False means "not enabled" — treat as not set
            if target_value is not None and target_value is not False:
                raise RuleViolationError(rule.error_message)
            return

        if rule.rule_type == RuleType.RESTRICTS_VALUE:
            if target_value is None:
                return  # optional attribute not provided — nothing to restrict
            allowed_values = set(rule.allowed_values or [])
            if str(target_value) not in allowed_values:
                raise RuleViolationError(rule.error_message)
            return

        raise RuleViolationError(f"Unsupported rule type: {rule.rule_type}")