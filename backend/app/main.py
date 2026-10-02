import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from backend.app.core.limiter import limiter

from backend.app.config import settings
from backend.app.database import init_db, SessionLocal
from backend.app.core.logging_config import logger
from backend.app.routers import (
    auth,
    doctors,
    patients,
    appointments,
    payments,
    notifications,
    feedback,
    reports,
    admin
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Doctor Appointment Management System Database...")
    init_db()
    # Check if seed data is needed
    try:
        from backend.seed_data import seed_database
        db = SessionLocal()
        seed_database(db)
        db.close()
    except Exception as e:
        logger.warning(f"Seed execution check: {e}")
    yield
    logger.info("Application shutdown.")

app = FastAPI(
    title="Doctor Appointment Management System API",
    description="Full-stack Healthcare Appointment Platform conforming to Software Engineering Lab Manuals (Experiments 1-11)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers (Experiment 8, 11)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred. Please contact system administrator."}
    )

# Register API Routers
app.include_router(auth.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/")
def root():
    return {
        "system": "Doctor Appointment Management System",
        "status": "online",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }
