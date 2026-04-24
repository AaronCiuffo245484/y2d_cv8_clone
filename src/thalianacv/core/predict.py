# thalianacv/core/predict.py
"""Core inference pipeline for thalianacv.

This module exposes the primary public interface of the package. All consumers
(API, CLI, database) should call predict() rather than invoking the data or
model submodules directly.

predict() is currently a stub. It returns a PredictionResult populated
with sentinel values and does not load any models or process any images.
Sentinel values are deliberately invalid to make stub behaviour detectable.
shoot_mask and root_mask are arrays filled with -1, coordinates is a
DataFrame with correct columns and all values set to -999.0, and
confidence_score is -1.0.

Example:
    >>> from pathlib import Path
    >>> from thalianacv.core.predict import predict
    >>> result = predict(
    ...     image_path=Path("image.png"),
    ...     shoot_model_path=Path("shoot.h5"),
    ...     root_model_path=Path("root.h5"),
    ... )
    >>> print(result.confidence_score)  # -1.0 in stub
"""

from pathlib import Path

import numpy as np

from thalianacv.utils.logging import get_logger
from thalianacv.utils.types import PredictionResult

logger = get_logger(__name__)

# Default stats path bundled with the package.
# Loaded automatically when global_stats_path=None is passed to predict().
_DEFAULT_STATS_PATH = Path(__file__).parent.parent / "data" / "default_stats.json"


def predict(
    image_path: str | Path,
    shoot_model_path: str | Path,
    root_model_path: str | Path,
    global_stats_path: str | Path | None = None,
) -> PredictionResult:
    """Run the full inference pipeline on a single plant image.

    Accepts a raw plant image and two trained segmentation models (shoot and
    root). Returns segmentation masks, per-plant coordinates, and a confidence
    score derived from raw model probabilities.

    When global_stats_path is None, loads bundled default stats from
    thalianacv/data/default_stats.json. To use updated stats produced by the
    retraining pipeline, pass a path to a replacement JSON file with the same
    schema.

    Args:
        image_path: Path to the input plant image file.
        shoot_model_path: Path to the trained shoot segmentation model (.h5).
        root_model_path: Path to the trained root segmentation model (.h5).
        global_stats_path: Path to a JSON file containing global Y-pixel
            statistics for shoot mask quality validation. If None, uses
            the bundled default at thalianacv/data/default_stats.json.

    Returns:
        PredictionResult containing:
            - shoot_mask: Binary shoot segmentation mask (H, W) numpy array.
            - root_mask: Binary root segmentation mask (H, W) numpy array.
            - coordinates: DataFrame with 5 rows, one per plant, containing
              root lengths and pixel/robot coordinates.
            - confidence_score: Mean foreground prediction probability in
              range [0.0, 1.0]. Returns -1.0 in stub.

    Raises:
        ThalianaCVError: If any required file path does not exist.
        ThalianaCVError: If the image cannot be loaded.
        ThalianaCVError: If either model cannot be loaded.

    Example:
        >>> result = predict(
        ...     image_path="plate_01.png",
        ...     shoot_model_path="shoot.h5",
        ...     root_model_path="root.h5",
        ... )
        >>> print(result.confidence_score)
        >>> print(result.coordinates[["plant_order", "Length (px)"]])
    """
    image_path = Path(image_path)
    shoot_model_path = Path(shoot_model_path)
    root_model_path = Path(root_model_path)

    if global_stats_path is None:
        global_stats_path = _DEFAULT_STATS_PATH
    else:
        global_stats_path = Path(global_stats_path)

    logger.info("predict() called -- running as stub")
    logger.info("image_path: %s", image_path)
    logger.info("shoot_model_path: %s", shoot_model_path)
    logger.info("root_model_path: %s", root_model_path)
    logger.info("global_stats_path: %s", global_stats_path)

    # TODO: replace with real implementation
    # Step 1: load and validate image
    # Step 2: load global stats from global_stats_path
    # Step 3: run shoot inference via thalianacv.models.inference
    # Step 4: run root inference via thalianacv.models.inference
    # Step 5: clean shoot mask via thalianacv.data.preprocessing
    # Step 6: repair root mask via thalianacv.data.preprocessing
    # Step 7: run root-shoot matching via root_shoot_matching
    # Step 8: compute confidence score from raw model probabilities
    # Step 9: return PredictionResult

    stub_mask = np.full((512, 512), -1, dtype=np.int8)

    return PredictionResult(
        shoot_mask=stub_mask.copy(),
        root_mask=stub_mask.copy(),
        coordinates=PredictionResult.empty_coordinates(),
        confidence_score=-1.0,
    )
