from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from app.schemas.error import ErrorBody, ErrorResponse


def build_error_response(
    *,
    request: Request,
    status_code: int,
    error_type: str,
    message: str,
    code: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)

    payload = ErrorResponse(
        error=ErrorBody(
            type=error_type,
            message=message,
            code=code,
            request_id=request_id,
            details=details,
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(),
    )