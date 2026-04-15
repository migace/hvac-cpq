from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from app.core.family_config import FAMILY_CALCULATION_TYPE
from app.domain.exceptions import ConfigurationError
from app.schemas.technical_calculation import TechnicalCalculationItem


class TechnicalCalculationService:
    _CALCULATORS: dict[str, str] = {
        "rectangular": "_calculate_rectangular_fire_damper",
        "round": "_calculate_round_fire_damper",
    }

    def calculate(
        self,
        *,
        family_code: str,
        configuration_values: dict[str, Any],
    ) -> list[TechnicalCalculationItem]:
        calc_type = FAMILY_CALCULATION_TYPE.get(family_code)
        if calc_type is None:
            raise ConfigurationError(
                f"Technical calculations are not implemented for family '{family_code}'."
            )

        method = getattr(self, self._CALCULATORS[calc_type])
        return method(configuration_values)

    def _calculate_rectangular_fire_damper(
        self,
        values: dict[str, Any],
    ) -> list[TechnicalCalculationItem]:
        width = self._required_int(values, "width")
        height = self._required_int(values, "height")

        area_m2 = (
            Decimal(width) * Decimal(height) / Decimal("1000000")
        ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        return [
            TechnicalCalculationItem(
                name="Effective area",
                code="effective_area",
                value=area_m2,
                unit="m2",
            )
        ]

    def _calculate_round_fire_damper(
        self,
        values: dict[str, Any],
    ) -> list[TechnicalCalculationItem]:
        diameter = self._required_int(values, "diameter")

        radius_m = Decimal(diameter) / Decimal("2000")
        area_m2 = (
            Decimal("3.1415926535") * radius_m * radius_m
        ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        return [
            TechnicalCalculationItem(
                name="Effective area",
                code="effective_area",
                value=area_m2,
                unit="m2",
            )
        ]

    def _required_int(self, values: dict[str, Any], key: str) -> int:
        value = values.get(key)
        if value is None:
            raise ConfigurationError(
                f"Attribute '{key}' is required to calculate technical parameters."
            )
        if not isinstance(value, int):
            raise ConfigurationError(
                f"Attribute '{key}' must be an integer for technical calculations."
            )
        return value