# tests/test_api.py
"""Integration tests for the thalianacv inference API.
Tests cover the /health and /predict endpoints using FastAPI's TestClient.
These tests run against the application directly without requiring a live server.
To run:
    uv run pytest tests/test_api.py -v
"""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from thalianacv.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def make_test_image(fmt: str = "PNG") -> bytes:
    """Create a minimal in-memory image for use in tests.

    Args:
        fmt: Image format string, e.g. 'PNG', 'JPEG'.

    Returns:
        Raw image bytes in the specified format.
    """
    img = Image.new("RGB", (64, 64), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_health_returns_200(client):
    """GET /health returns HTTP 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_valid_image_returns_200(client):
    """POST /predict with a valid PNG returns HTTP 200 with expected fields."""
    image_bytes = make_test_image("PNG")
    response = client.post(
        "/predict",
        files={"file": ("test_image.png", image_bytes, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert "confidence_score" in body
    assert "coordinates" in body
    assert "mask_shape" in body
    assert "submission_id" in body
    assert "prediction_id" in body


def test_predict_stub_returns_sentinel_values(client):
    """POST /predict returns stub sentinel values while inference is not implemented."""
    image_bytes = make_test_image("PNG")
    response = client.post(
        "/predict",
        files={"file": ("test_image.png", image_bytes, "image/png")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["confidence_score"] == -1.0
    assert body["submission_id"] == -1
    assert body["prediction_id"] == -1


def test_predict_wrong_file_type_returns_400(client):
    """POST /predict with a non-image file returns HTTP 400."""
    response = client.post(
        "/predict",
        files={"file": ("document.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400


def test_predict_missing_file_returns_422(client):
    """POST /predict with no file attached returns HTTP 422."""
    response = client.post("/predict")
    assert response.status_code == 422
