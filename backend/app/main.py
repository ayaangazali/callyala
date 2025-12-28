"""
Voice Agent Ops - FastAPI Application

Main entry point for the Voice Agent Ops backend API.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import (
    generate_request_id,
    get_logger,
    set_request_id,
    setup_logging,
)
from app.db.session import close_db, init_db

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting Voice Agent Ops API")
    await init_db()
    yield
    logger.info("Shutting down Voice Agent Ops API")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Voice Agent Ops",
    description="AI voice agent platform for automotive dealerships",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Add request ID to all requests for tracing."""
    request_id = generate_request_id()
    set_request_id(request_id)

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    return response


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "voice-agent-ops"}


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness check - verify dependencies are available."""
    # TODO: Add database and Redis connectivity checks
    return {"status": "ready"}


# Import and include routers
from app.api.routes import (
    appointments,
    auth,
    calls,
    campaigns,
    customers,
    overview,
    scripts,
    webhooks_elevenlabs,
)

app.include_router(auth.router, prefix="/api")
app.include_router(overview.router, prefix="/api")
app.include_router(calls.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(scripts.router, prefix="/api")
app.include_router(webhooks_elevenlabs.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Run with: uvicorn app.main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
