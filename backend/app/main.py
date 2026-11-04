from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import logger
from app.database.init_db import init_db

# Import routers
from app.api.health import router as health_router
from app.api.dashboard import router as dashboard_router
from app.api.inspection import router as inspection_router
from app.api.datasets import router as datasets_router
from app.api.models import router as models_router
from app.api.reports import router as reports_router
from app.api.analytics import router as analytics_router
from app.api.settings import router as settings_router

# Ensure database tables and catalogs are initialized
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup sequence: initializes database tables, seeds dataset catalog,
    registers baseline detection models, and prepares demo sample images.
    """
    logger.info("Starting up Industrial Quality Inspector Backend Service...")
    init_db()
    yield
    logger.info("Shutting down Industrial Quality Inspector Backend Service.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Multimodal AI-Based Industrial Quality Inspection and Defect Explanation System REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for inspection images, datasets, and generated PDF reports
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")
app.mount("/reports", StaticFiles(directory=str(settings.REPORTS_DIR)), name="reports")
app.mount("/datasets-static", StaticFiles(directory=str(settings.DATASETS_DIR)), name="datasets-static")

# Include API Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(inspection_router, prefix="/api")
app.include_router(datasets_router, prefix="/api")
app.include_router(models_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(settings_router, prefix="/api")

@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "documentation": "/docs",
        "health_check": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
