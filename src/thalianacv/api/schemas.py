# src/thalianacv/api/schemas.py
"""Pydantic schemas for the thalianacv API.

Defines request and response models for all API endpoints.
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response schema for the /health endpoint."""

    status: str


class CoordinateRow(BaseModel):
    """A single row of root-tip coordinate data for one plant."""

    plant_order: int
    length_px: float
    x_px: float
    y_px: float


class PredictionResponse(BaseModel):
    """Response schema for the POST /predict endpoint."""

    submission_id: int
    prediction_id: int
    confidence_score: float
    coordinates: list[CoordinateRow]
    mask_shape: list[int]
    message: str
