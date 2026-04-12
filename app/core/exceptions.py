from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from typing import Any

from app.core.error_response import build_error_response
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
    ProductQuoteNotFoundError,
    ProductRuleDefinitionError,
    RuleViolationError,
)

logger = get_logger()


def _serialize_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    serialized_errors: list[dict[str, Any]] = []

    for error in errors:
        normalized_error: dict[str, Any] = {}

        for key, value in error.items():
            if key == "ctx" and isinstance(value, dict):
                normalized_error[key] = {
                    ctx_key: str(ctx_value)
                    for ctx_key, ctx_value in value.items()
                }
            elif isinstance(value, tuple):
                normalized_error[key] = list(value)
            else:
                normalized_error[key] = value

        serialized_errors.append(normalized_error)

    return serialized_errors


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
            request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning(
            "request_validation_error",
            errors=exc.errors(),
            body=getattr(exc, "body", None),
        )
        serialized_errors = _serialize_validation_errors(exc.errors())

        return build_error_response(
            request=request,
            status_code=422,
            error_type="RequestValidationError",
            message="Request payload validation failed.",
            code="request_validation_error",
            details={"errors": serialized_errors},
        )

    @app.exception_handler(ProductFamilyAlreadyExistsError)
    async def handle_product_family_exists(
            request: Request, exc: ProductFamilyAlreadyExistsError
    ) -> JSONResponse:
        logger.warning("product_family_exists", error=str(exc))
        return build_error_response(
            request=request,
            status_code=409,
            error_type=type(exc).__name__,
            message=str(exc),
            code="product_family_already_exists",
        )

    @app.exception_handler(ProductFamilyNotFoundError)
    async def handle_product_family_not_found(
            request: Request, exc: ProductFamilyNotFoundError
    ) -> JSONResponse:
        logger.warning("product_family_not_found", error=str(exc))
        return build_error_response(
            request=request,
            status_code=404,
            error_type=type(exc).__name__,
            message=str(exc),
            code="product_family_not_found",
        )

    @app.exception_handler(ProductConfigurationNotFoundError)
    async def handle_product_configuration_not_found(
            request: Request, exc: ProductConfigurationNotFoundError
    ) -> JSONResponse:
        logger.warning("product_configuration_not_found", error=str(exc))
        return build_error_response(
            request=request,
            status_code=404,
            error_type=type(exc).__name__,
            message=str(exc),
            code="product_configuration_not_found",
        )

    @app.exception_handler(ProductQuoteNotFoundError)
    async def handle_product_quote_not_found(
            request: Request, exc: ProductQuoteNotFoundError
    ) -> JSONResponse:
        logger.warning("product_quote_not_found", error=str(exc))
        return build_error_response(
            request=request,
            status_code=404,
            error_type=type(exc).__name__,
            message=str(exc),
            code="product_quote_not_found",
        )

    @app.exception_handler(AttributeDefinitionNotFoundError)
    async def handle_attribute_definition_not_found(
            request: Request, exc: AttributeDefinitionNotFoundError
    ) -> JSONResponse:
        logger.warning("attribute_definition_not_found", error=str(exc))
        return build_error_response(
            request=request,
            status_code=400,
            error_type=type(exc).__name__,
            message=str(exc),
            code="attribute_definition_not_found",
        )

    @app.exception_handler(InvalidAttributeValueError)
    async def handle_invalid_attribute_value(
            request: Request, exc: InvalidAttributeValueError
    ) -> JSONResponse:
        logger.warning("invalid_attribute_value", error=str(exc))
        return build_error_response(
            request=request,
            status_code=400,
            error_type=type(exc).__name__,
            message=str(exc),
            code="invalid_attribute_value",
        )

    @app.exception_handler(MissingRequiredAttributesError)
    async def handle_missing_required_attributes(
            request: Request, exc: MissingRequiredAttributesError
    ) -> JSONResponse:
        logger.warning("missing_required_attributes", error=str(exc), missing=exc.missing)
        return build_error_response(
            request=request,
            status_code=400,
            error_type=type(exc).__name__,
            message=str(exc),
            code="missing_required_attributes",
            details={"missing_attributes": exc.missing},
        )

    @app.exception_handler(EmptyConfigurationError)
    async def handle_empty_configuration(
            request: Request, exc: EmptyConfigurationError
    ) -> JSONResponse:
        logger.warning("empty_configuration", error=str(exc))
        return build_error_response(
            request=request,
            status_code=400,
            error_type=type(exc).__name__,
            message=str(exc),
            code="empty_configuration",
        )

    @app.exception_handler(ProductRuleDefinitionError)
    async def handle_product_rule_definition_error(
            request: Request, exc: ProductRuleDefinitionError
    ) -> JSONResponse:
        logger.warning("product_rule_definition_error", error=str(exc))
        return build_error_response(
            request=request,
            status_code=400,
            error_type=type(exc).__name__,
            message=str(exc),
            code="product_rule_definition_error",
        )

    @app.exception_handler(RuleViolationError)
    async def handle_rule_violation_error(
            request: Request, exc: RuleViolationError
    ) -> JSONResponse:
        logger.warning("rule_violation_error", error=str(exc))
        return build_error_response(
            request=request,
            status_code=400,
            error_type=type(exc).__name__,
            message=str(exc),
            code="rule_violation",
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(
            request: Request, exc: IntegrityError
    ) -> JSONResponse:
        logger.exception("integrity_error", error=str(exc))
        return build_error_response(
            request=request,
            status_code=409,
            error_type="IntegrityError",
            message="Database integrity constraint violated.",
            code="database_integrity_error",
        )

    @app.exception_handler(SQLAlchemyError)
    async def handle_sqlalchemy_error(
            request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.exception("sqlalchemy_error", error=str(exc))
        return build_error_response(
            request=request,
            status_code=500,
            error_type="DatabaseError",
            message="A database error occurred.",
            code="database_error",
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning("domain_error", error=str(exc), error_type=type(exc).__name__)
        return build_error_response(
            request=request,
            status_code=400,
            error_type=type(exc).__name__,
            message=str(exc),
            code="domain_error",
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
            request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("unexpected_error", error=str(exc), error_type=type(exc).__name__)
        return build_error_response(
            request=request,
            status_code=500,
            error_type="InternalServerError",
            message="An unexpected error occurred.",
            code="internal_server_error",
        )
