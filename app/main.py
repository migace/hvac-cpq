from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, configure_logging
from app.observability.tracing import configure_tracing

configure_logging()
logger = get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_starting", app_name=settings.app_name, env=settings.app_env)
    configure_tracing(app)
    yield
    logger.info("application_stopping", app_name=settings.app_name, env=settings.app_env)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    app.include_router(health_router)

    return app


app = create_app()
