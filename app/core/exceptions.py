from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.domain.exceptions import (
    AttributeDefinitionNotFoundError,
    DomainError,
    EmptyConfigurationError,
    InvalidAttributeValueError,
    MissingRequiredAttributesError,
    ProductConfigurationNotFoundError,
    ProductFamilyAlreadyExistsError,
    ProductFamilyNotFoundError,
    ProductRuleDefinitionError,
    RuleViolationError,
    ProductQuoteNotFoundError
)

logger = get_logger()


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProductFamilyAlreadyExistsError)
    async def handle_product_family_exists(
            _: Request, exc: ProductFamilyAlreadyExistsError
    ) -> JSONResponse:
        logger.warning("product_family_exists", error=str(exc))
        return JSONResponse(
            status_code=409,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(ProductFamilyNotFoundError)
    async def handle_product_family_not_found(
            _: Request, exc: ProductFamilyNotFoundError
    ) -> JSONResponse:
        logger.warning("product_family_not_found", error=str(exc))
        return JSONResponse(
            status_code=404,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(ProductConfigurationNotFoundError)
    async def handle_product_configuration_not_found(
            _: Request, exc: ProductConfigurationNotFoundError
    ) -> JSONResponse:
        logger.warning("product_configuration_not_found", error=str(exc))
        return JSONResponse(
            status_code=404,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(AttributeDefinitionNotFoundError)
    async def handle_attribute_definition_not_found(
            _: Request, exc: AttributeDefinitionNotFoundError
    ) -> JSONResponse:
        logger.warning("attribute_definition_not_found", error=str(exc))
        return JSONResponse(
            status_code=400,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(InvalidAttributeValueError)
    async def handle_invalid_attribute_value(
            _: Request, exc: InvalidAttributeValueError
    ) -> JSONResponse:
        logger.warning("invalid_attribute_value", error=str(exc))
        return JSONResponse(
            status_code=400,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(MissingRequiredAttributesError)
    async def handle_missing_required_attributes(
            _: Request, exc: MissingRequiredAttributesError
    ) -> JSONResponse:
        logger.warning("missing_required_attributes", error=str(exc))
        return JSONResponse(
            status_code=400,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(EmptyConfigurationError)
    async def handle_empty_configuration(
            _: Request, exc: EmptyConfigurationError
    ) -> JSONResponse:
        logger.warning("empty_configuration", error=str(exc))
        return JSONResponse(
            status_code=400,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        logger.warning("domain_error", error=str(exc), error_type=type(exc).__name__)
        return JSONResponse(
            status_code=400,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unexpected_error", error=str(exc), error_type=type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred.",
                }
            },
        )

    @app.exception_handler(ProductRuleDefinitionError)
    async def handle_product_rule_definition_error(
            _: Request, exc: ProductRuleDefinitionError
    ) -> JSONResponse:
        logger.warning("product_rule_definition_error", error=str(exc))
        return JSONResponse(
            status_code=400,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(RuleViolationError)
    async def handle_rule_violation_error(
            _: Request, exc: RuleViolationError
    ) -> JSONResponse:
        logger.warning("rule_violation_error", error=str(exc))
        return JSONResponse(
            status_code=400,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )

    @app.exception_handler(ProductQuoteNotFoundError)
    async def handle_product_quote_not_found(
            _: Request, exc: ProductQuoteNotFoundError
    ) -> JSONResponse:
        logger.warning("product_quote_not_found", error=str(exc))
        return JSONResponse(
            status_code=404,
            content={"error": {"type": type(exc).__name__, "message": str(exc)}},
        )
