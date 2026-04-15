from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.product_families import router as product_families_router
from app.api.routes.product_configurations import router as product_configurations_router
from app.api.routes.product_rules import router as product_rules_router
from app.api.routes.product_pricing_rules import router as product_pricing_rules_router
from app.api.routes.product_quotes import router as product_quotes_router
from app.api.routes.agent import router as agent_router

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, configure_logging
from app.observability.tracing import configure_tracing

from app.core.http_logging import HttpLoggingMiddleware
from app.core.request_context import RequestContextMiddleware

configure_logging()
logger = get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_starting",
                app_name=settings.app_name, env=settings.app_env)
    configure_tracing(app)
    yield
    logger.info("application_stopping",
                app_name=settings.app_name, env=settings.app_env)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(HttpLoggingMiddleware)

    # CORS configuration — add last so it executes first in the middleware chain
    # In production, restrict to specific domains
    allowed_origins = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000"
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in allowed_origins],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(product_families_router)
    app.include_router(product_configurations_router)
    app.include_router(product_rules_router)
    app.include_router(product_pricing_rules_router)
    app.include_router(product_quotes_router)
    app.include_router(agent_router)

    return app


app = create_app()
