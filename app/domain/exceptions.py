class DomainError(Exception):
    """Base class for domain-related errors."""


class ConfigurationError(DomainError):
    """Raised when a product configuration is invalid."""


class RuleEvaluationError(DomainError):
    """Raised when a business rule cannot be evaluated."""