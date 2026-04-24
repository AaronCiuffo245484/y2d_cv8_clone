# src/thalianacv/api/main.py
"""FastAPI application entry point for the thalianacv inference service.

Creates and configures the FastAPI application instance. All routes
are registered via the router defined in thalianacv.api.routes.

Example:
    Run the development server with uvicorn:

        uvicorn thalianacv.api.main:app --reload
"""

from fastapi import FastAPI

from thalianacv.api.routes import router
from thalianacv.utils.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="thalianacv Inference API",
    description=(
        "Plant segmentation and root-tip detection API"
        " for the HADES phenotyping system."
    ),
    version="0.2.0",
)

app.include_router(router)

logger.info("thalianacv API started")
