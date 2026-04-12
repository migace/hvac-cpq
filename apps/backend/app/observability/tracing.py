from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger()


def configure_tracing(app: FastAPI) -> None:
    settings = get_settings()

    if not settings.otel_enabled:
        logger.info("tracing_disabled")
        return

    logger.info("tracing_enabled_placeholder")