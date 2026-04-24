# tests/test_api_schemas.py
"""Unit tests for thalianacv.api.schemas."""

import pytest  # noqa: F401
from pydantic import ValidationError

from thalianacv.api.schemas import CoordinateRow, HealthResponse, PredictionResponse

# --- HealthResponse ---


def test_health_response_valid():
    """HealthResponse accepts a valid status string."""
    response = HealthResponse(status="ok")
    assert response.status == "ok"


def test_health_response_missing_status_raises():
    """HealthResponse raises ValidationError when status is missing."""
    with pytest.raises(ValidationError):
        HealthResponse()


# --- CoordinateRow ---


def test_coordinate_row_valid():
    """CoordinateRow accepts valid numeric fields."""
    row = CoordinateRow(plant_order=1, length_px=10.5, x_px=100.0, y_px=200.0)
    assert row.plant_order == 1
    assert row.length_px == 10.5


def test_coordinate_row_sentinel_values():
    """CoordinateRow accepts stub sentinel values."""
    row = CoordinateRow(plant_order=1, length_px=-999.0, x_px=0.0, y_px=0.0)
    assert row.length_px == -999.0


def test_coordinate_row_missing_field_raises():
    """CoordinateRow raises ValidationError when a required field is missing."""
    with pytest.raises(ValidationError):
        CoordinateRow(plant_order=1, length_px=10.5)


# --- PredictionResponse ---


def test_prediction_response_valid():
    """PredictionResponse accepts valid fields including coordinate list."""
    response = PredictionResponse(
        submission_id=-1,
        prediction_id=-1,
        confidence_score=-1.0,
        coordinates=[
            CoordinateRow(plant_order=1, length_px=-999.0, x_px=0.0, y_px=0.0)
        ],
        mask_shape=[512, 512],
        message="Prediction complete",
    )
    assert response.submission_id == -1
    assert len(response.coordinates) == 1


def test_prediction_response_empty_coordinates():
    """PredictionResponse accepts an empty coordinates list."""
    response = PredictionResponse(
        submission_id=-1,
        prediction_id=-1,
        confidence_score=-1.0,
        coordinates=[],
        mask_shape=[512, 512],
        message="Prediction complete",
    )
    assert response.coordinates == []


def test_prediction_response_missing_field_raises():
    """PredictionResponse raises ValidationError when a required field is missing."""
    with pytest.raises(ValidationError):
        PredictionResponse(
            submission_id=-1,
            confidence_score=-1.0,
        )
