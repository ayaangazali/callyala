"""Voice Agent Ops - FastAPI Application."""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger, request_id_ctx
from app.services.elevenlabs import elevenlabs

# Import routers
from app.api.routes.health import router as health_router
from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.calls import router as calls_router
from app.api.routes.overview import router as overview_router
from app.api.routes.webhooks import router as webhooks_router
from app.api.routes.sheets import router as sheets_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting Voice Agent Ops (env={settings.app_env}, mock={settings.mock_mode})")
    yield
    logger.info("Shutting down Voice Agent Ops")
    await elevenlabs.close()


app = FastAPI(
    title="Voice Agent Ops",
    description="AI Voice Agent Operations Platform for Car Dealerships",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add request ID to all requests."""
    rid = str(uuid.uuid4())[:8]
    request_id_ctx.set(rid)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


# Register routers
app.include_router(health_router)
app.include_router(campaigns_router)
app.include_router(calls_router)
app.include_router(overview_router)
app.include_router(webhooks_router)
app.include_router(sheets_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Voice Agent Ops",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
