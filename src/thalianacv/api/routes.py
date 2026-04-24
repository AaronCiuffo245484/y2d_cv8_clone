# src/thalianacv/api/routes.py
"""API route definitions for the thalianacv inference service.

Defines the /health and /predict endpoints. All database operations
are delegated to thalianacv.database.models. All inference operations
are delegated to thalianacv.core.predict.
"""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from thalianacv.api.schemas import CoordinateRow, HealthResponse, PredictionResponse
from thalianacv.core.predict import predict
from thalianacv.database.models import save_prediction, save_submission
from thalianacv.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/tiff"}


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Check that the API service is running.

    Returns:
        HealthResponse with status set to 'ok'.
    """
    logger.info("Health check requested")
    return HealthResponse(status="ok")


@router.post("/predict", response_model=PredictionResponse)
def predict_endpoint(file: UploadFile = File(...)) -> PredictionResponse:
    """Accept a plant image and return segmentation results.

    Validates the uploaded file is an image, runs the inference pipeline,
    saves submission and prediction metadata to the database, and returns
    structured results.

    Args:
        file: Uploaded image file. Must be JPEG, PNG, or TIFF.

    Returns:
        PredictionResponse containing confidence score, coordinates,
        mask shape, and database record IDs.

    Raises:
        HTTPException: 400 if the file is missing or not a supported image type.
        HTTPException: 500 if inference or database operations fail.
    """
    logger.info("POST /predict called with file: %s", file.filename)

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        logger.warning(
            "Rejected file %s with content type %s", file.filename, file.content_type
        )
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {file.content_type}."
                " Must be JPEG, PNG, or TIFF."
            ),
        )

    try:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(file.filename).suffix
        ) as tmp:
            tmp.write(file.file.read())
            tmp_path = Path(tmp.name)

        logger.info("Saved upload to temp file: %s", tmp_path)

        submission_id = save_submission(image_path=tmp_path, user_id="anonymous")
        logger.info("Saved submission with ID: %s", submission_id)

        result = predict(
            image_path=tmp_path,
            shoot_model_path=Path("models/shoot.h5"),
            root_model_path=Path("models/root.h5"),
        )
        logger.info("Inference complete, confidence: %s", result.confidence_score)

        prediction_id = save_prediction(submission_id=submission_id, result=result)
        logger.info("Saved prediction with ID: %s", prediction_id)

        coordinates = [
            CoordinateRow(
                plant_order=int(row["plant_order"]),
                length_px=float(row.get("Length (px)", 0.0)),
                x_px=float(row.get("x_px", 0.0)),
                y_px=float(row.get("y_px", 0.0)),
            )
            for row in result.coordinates.to_dict(orient="records")
        ]

        return PredictionResponse(
            submission_id=submission_id,
            prediction_id=prediction_id,
            confidence_score=result.confidence_score,
            coordinates=coordinates,
            mask_shape=list(result.shoot_mask.shape),
            message="Prediction complete",
        )

    except Exception as e:
        logger.error("Prediction failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
