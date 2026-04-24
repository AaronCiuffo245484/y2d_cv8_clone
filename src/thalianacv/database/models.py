# thalianacv/database/models.py
"""Database operation stubs for thalianacv.

This module contains all database functions. It is the single point of
contact for PostgreSQL operations across the package. No other submodule
should interact with the database directly.

All functions in this module are stubs. They return sentinel values and
do not connect to a database. Sentinel values are deliberately invalid
to make stub behaviour detectable. Integer IDs return -1, functions
returning None behave correctly, and functions returning lists return
an empty list.

The database owner should replace each stub body with a real implementation
using SQLAlchemy or psycopg2. Connection configuration should be loaded
via a config file rather than hardcoded credentials.

Example:
    >>> from thalianacv.database import save_submission, save_prediction
    >>> submission_id = save_submission("image.png", "user_01")
    >>> prediction_id = save_prediction(submission_id, result)
"""

from pathlib import Path

from thalianacv.utils.logging import get_logger
from thalianacv.utils.types import PredictionResult

logger = get_logger(__name__)


def save_submission(image_path: str | Path, user_id: str) -> int:
    """Save a new image submission and return the generated submission ID.

    Args:
        image_path: Path to the submitted image file.
        user_id: Identifier of the user submitting the image.

    Returns:
        Generated submission ID as an integer.
        Returns -1 when running as a stub.

    Example:
        >>> submission_id = save_submission("image.png", "user_01")
        >>> assert submission_id > 0  # will fail on stub
    """
    logger.warning("save_submission is a stub -- no data written to database")
    return -1


def save_prediction(submission_id: int, result: PredictionResult) -> int:
    """Save prediction results linked to a submission.

    Args:
        submission_id: ID of the submission this prediction belongs to.
        result: PredictionResult instance returned by thalianacv.core.predict.

    Returns:
        Generated prediction ID as an integer.
        Returns -1 when running as a stub.

    Example:
        >>> prediction_id = save_prediction(1, result)
        >>> assert prediction_id > 0  # will fail on stub
    """
    logger.warning("save_prediction is a stub -- no data written to database")
    return -1


def save_correction(
    prediction_id: int,
    is_correct: bool,
    annotation: dict | None = None,
) -> None:
    """Record user feedback on a prediction.

    Args:
        prediction_id: ID of the prediction being corrected.
        is_correct: True if the prediction was correct, False otherwise.
        annotation: Optional dict containing annotation data, e.g.
            corrected coordinates or mask paths.

    Returns:
        None.

    Example:
        >>> save_correction(1, is_correct=False, annotation={"note": "root missed"})
    """
    logger.warning("save_correction is a stub -- no data written to database")


def get_submissions(user_id: str) -> list[dict]:
    """Retrieve all submissions for a given user.

    Args:
        user_id: Identifier of the user whose submissions to retrieve.

    Returns:
        List of dicts, one per submission. Each dict contains submission
        metadata (id, image_path, timestamp, user_id).
        Returns an empty list when running as a stub.

    Example:
        >>> submissions = get_submissions("user_01")
        >>> for s in submissions:
        ...     print(s["id"], s["image_path"])
    """
    logger.warning("get_submissions is a stub -- returning empty list")
    return []


def get_corrections() -> list[dict]:
    """Retrieve all flagged corrections for use by the retraining pipeline.

    Returns:
        List of dicts, one per correction. Each dict contains prediction_id,
        is_correct, annotation, and timestamp.
        Returns an empty list when running as a stub.

    Example:
        >>> corrections = get_corrections()
        >>> for c in corrections:
        ...     print(c["prediction_id"], c["is_correct"])
    """
    logger.warning("get_corrections is a stub -- returning empty list")
    return []
