class DomainError(Exception):
    """Base class for domain-related errors."""


class ConfigurationError(DomainError):
    """Raised when a product configuration is invalid."""


class RuleEvaluationError(DomainError):
    """Raised when a business rule cannot be evaluated."""


class ProductFamilyAlreadyExistsError(DomainError):
    """Raised when a product family with the same code already exists."""


class ProductFamilyNotFoundError(DomainError):
    """Raised when a product family does not exist."""


class AttributeDefinitionNotFoundError(DomainError):
    """Raised when an attribute definition does not exist in the selected family."""


class InvalidAttributeValueError(DomainError):
    """Raised when an attribute value does not match attribute definition."""


class ProductConfigurationNotFoundError(DomainError):
    """Raised when a product configuration does not exist."""


class MissingRequiredAttributesError(ConfigurationError):
    """Raised when required attributes are missing in configuration."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__("Missing required attributes: " + ", ".join(missing))


class EmptyConfigurationError(ConfigurationError):
    """Raised when configuration has no values."""


class RuleViolationError(ConfigurationError):
    """Raised when configuration violates a business rule."""


class ProductRuleDefinitionError(DomainError):
    """Raised when a product rule references invalid family attributes."""


class ProductQuoteNotFoundError(DomainError):
    """Raised when a quote does not exist."""


class CurrencyMismatchError(DomainError):
    """Raised when pricing rules for a family use inconsistent currencies."""