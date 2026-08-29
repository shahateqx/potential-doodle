"""FastAPI application — Embeddable Widget & Lead-Capture Platform.

Assembles all routers, middleware (CORS, rate limiting), and error handlers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.middleware.rate_limiter import limiter
from app.routers import auth, widgets, submissions, dashboard, public

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    logger.info("🚀 Widget Platform starting up...")
    yield
    logger.info("👋 Widget Platform shutting down...")


# Create the FastAPI application
app = FastAPI(
    title="Embeddable Widget & Lead-Capture Platform",
    description=(
        "A platform that lets customers create embeddable widgets "
        "(signup forms, contact forms, CTA popovers) and install them "
        "on any website with a single <script> tag."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ─── Rate Limiter ─────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS Middleware ──────────────────────────
# Allow any origin for the public submission and widget delivery endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Widget-Version", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=3600,  # Cache preflight for 1 hour
)

# ─── Routers ──────────────────────────────────
app.include_router(auth.router)
app.include_router(widgets.router)
app.include_router(submissions.router)
app.include_router(dashboard.router)
app.include_router(public.router)


# ─── Global Error Handlers ───────────────────
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """Ensure validation errors return clean JSON, never a 500."""
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": str(exc)},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Log internal errors and return a clean JSON response."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ─── Health Check ─────────────────────────────
@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
