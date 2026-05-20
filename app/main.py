# app/main.py
"""Main application entrypoint for TalaTrivia API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import answers, auth, questions, trivias, users
from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    ResourceNotFoundException,
    UnauthorizedException,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


# ======================================================
# APPLICATION LIFESPAN
# ======================================================
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown lifecycle."""

    logger.info(
        "Starting application '%s' in '%s' mode",
        settings.APP_NAME,
        settings.APP_ENV,
    )

    yield

    logger.info("Shutting down application '%s'", settings.APP_NAME)


# ======================================================
# FASTAPI APPLICATION
# ======================================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    lifespan=lifespan,
)


# ======================================================
# CORS
# ======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================================
# ROUTERS
# ======================================================
api_prefix = settings.API_V1_PREFIX

app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(questions.router, prefix=api_prefix)
app.include_router(trivias.router, prefix=api_prefix)
app.include_router(answers.router, prefix=api_prefix)


# ======================================================
# HEALTHCHECK
# ======================================================
@app.get("/health", tags=["system"], status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    """Simple healthcheck endpoint."""

    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
    }


# ======================================================
# EXCEPTION RESPONSE FACTORY
# ======================================================
def build_error_response(*, status_code: int, detail: str, code: str) -> JSONResponse:
    """Build standardized API error response."""

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "code": code,
        },
    )


# ======================================================
# DOMAIN EXCEPTION HANDLERS
# ======================================================
@app.exception_handler(ResourceNotFoundException)
async def resource_not_found_handler(
    _: Request, exc: ResourceNotFoundException
) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(exc),
        code="RESOURCE_NOT_FOUND",
    )


@app.exception_handler(BadRequestException)
async def bad_request_handler(_: Request, exc: BadRequestException) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
        code="BAD_REQUEST",
    )


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(_: Request, exc: UnauthorizedException) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=str(exc),
        code="UNAUTHORIZED",
    )


@app.exception_handler(ForbiddenException)
async def forbidden_handler(_: Request, exc: ForbiddenException) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=str(exc),
        code="FORBIDDEN",
    )


@app.exception_handler(ConflictException)
async def conflict_handler(_: Request, exc: ConflictException) -> JSONResponse:
    return build_error_response(
        status_code=status.HTTP_409_CONFLICT,
        detail=str(exc),
        code="CONFLICT",
    )


# ======================================================
# FALLBACK EXCEPTION HANDLER
# ======================================================
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch unexpected errors without leaking internal details.
    """

    logger.exception(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error": str(exc),
        },
    )

    return build_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected internal error occurred",
        code="INTERNAL_SERVER_ERROR",
    )
