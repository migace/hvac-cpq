from typing import Any

from app.domain.exceptions import ConfigurationError


class OrderCodeService:
    FAMILY_PREFIX_MAP = {
        "fire_damper": "FD",
        "fire_damper_rectangular": "FDR",
        "fire_damper_round": "FDO",
        "multi_blade_fire_damper": "MBF",
    }

    VALUE_CODE_MAP = {
        "reinforced": "REIN",
        "standard": "STD",
        "wall": "WALL",
        "ceiling": "CEIL",
    }

    def generate(
        self,
        *,
        family_code: str,
        configuration_values: dict[str, Any],
    ) -> str:
        prefix = self.FAMILY_PREFIX_MAP.get(family_code)
        if not prefix:
            raise ConfigurationError(
                f"No order code prefix configured for family '{family_code}'."
            )

        if family_code in {"fire_damper", "fire_damper_rectangular"}:
            return self._generate_rectangular_code(prefix, configuration_values)

        if family_code == "fire_damper_round":
            return self._generate_round_code(prefix, configuration_values)

        if family_code == "multi_blade_fire_damper":
            return self._generate_rectangular_code(prefix, configuration_values)

        raise ConfigurationError(
            f"Order code generation is not implemented for family '{family_code}'."
        )

    def _generate_rectangular_code(
        self,
        prefix: str,
        values: dict[str, Any],
    ) -> str:
        fire_class = self._required(values, "fire_class")
        width = self._required(values, "width")
        height = self._required(values, "height")
        actuator_type = self._optional_code(values.get("actuator_type"))
        installation_type = self._optional_code(values.get("installation_type"))

        parts = [
            prefix,
            str(fire_class),
            f"{width}x{height}",
        ]

        if actuator_type:
            parts.append(actuator_type)

        if installation_type:
            parts.append(installation_type)

        return "-".join(parts)

    def _generate_round_code(
        self,
        prefix: str,
        values: dict[str, Any],
    ) -> str:
        fire_class = self._required(values, "fire_class")
        diameter = self._required(values, "diameter")
        actuator_type = self._optional_code(values.get("actuator_type"))
        installation_type = self._optional_code(values.get("installation_type"))

        parts = [
            prefix,
            str(fire_class),
            f"D{diameter}",
        ]

        if actuator_type:
            parts.append(actuator_type)

        if installation_type:
            parts.append(installation_type)

        return "-".join(parts)

    def _required(self, values: dict[str, Any], key: str) -> Any:
        value = values.get(key)
        if value is None:
            raise ConfigurationError(
                f"Attribute '{key}' is required to generate order code."
            )
        return value

    def _optional_code(self, value: Any) -> str | None:
        if value is None:
            return None
        return self.VALUE_CODE_MAP.get(str(value), str(value).upper())