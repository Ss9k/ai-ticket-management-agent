"""
SupportPilot — FastAPI Backend Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_settings
from backend.core.logging_config import setup_logging
from backend.core.database import init_db
from backend.routers import auth, user, admin, engineer, analytics

# Configure logging first
setup_logging("INFO")
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler — startup and shutdown."""
    logger.info("=" * 60)
    logger.info("SupportPilot Backend Starting")
    logger.info("=" * 60)

    # Initialize database tables
    logger.info("Initialising database...")
    init_db()
    logger.info("Database ready")

    logger.info("SupportPilot Backend Ready")
    yield

    logger.info("SupportPilot Backend Shutting Down")


app = FastAPI(
    title="SupportPilot API",
    description="AI-Powered Enterprise IT Support & Ticket Management System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Flask frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(engineer.router)
app.include_router(analytics.router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SupportPilot API",
        "version": "1.0.0",
    }


@app.get("/")
def root():
    return {
        "message": "SupportPilot API",
        "docs": "/docs",
        "health": "/health",
    }
