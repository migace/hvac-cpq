from typing import Any

from pydantic import BaseModel


class ErrorBody(BaseModel):
    type: str
    message: str
    code: str
    request_id: str | None = None
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody