# tests/test_data_preprocessing_roi.py
"""Unit tests for thalianacv.data.preprocessing — ROI functions.

Tests are split into three groups:
    - Synthetic: generated on the fly, cover size/position variation
    - Real fixtures: three real HADES images in tests/fixtures/
    - TODO: placeholder tests requiring manual inspection
"""

from pathlib import Path

import cv2
import numpy as np
import pytest

from thalianacv.data.preprocessing import (
    crop_to_roi,
    detect_roi,
    ensure_grayscale,
    get_binary_mask,
    get_bounding_box,
)
from thalianacv.utils.logging import ThalianaCVError

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURE_IMAGES = [
    FIXTURES_DIR / "test_image_05.png",
    FIXTURES_DIR / "test_image_12.png",
    FIXTURES_DIR / "test_image_15.png",
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def grayscale_image():
    """100x100 grayscale image with a bright square in the centre."""
    image = np.zeros((100, 100), dtype=np.uint8)
    image[30:70, 30:70] = 200
    return image


@pytest.fixture
def bgr_image():
    """100x100 BGR colour image with a bright square in the centre."""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[30:70, 30:70] = (200, 200, 200)
    return image


def make_synthetic_image(height: int, width: int, radius: int, center=None):
    """Generate a synthetic grayscale image with a bright circle.

    Args:
        height: Image height in pixels.
        width: Image width in pixels.
        radius: Radius of the bright circle in pixels.
        center: (x, y) centre of the circle. Defaults to image centre.

    Returns:
        Grayscale numpy array with a bright circle on dark background.
    """
    image = np.zeros((height, width), dtype=np.uint8)
    if center is None:
        center = (width // 2, height // 2)
    cv2.circle(image, center, radius, 200, -1)
    return image


# ---------------------------------------------------------------------------
# ensure_grayscale
# ---------------------------------------------------------------------------


def test_ensure_grayscale_passthrough(grayscale_image):
    result = ensure_grayscale(grayscale_image)
    assert result.ndim == 2


def test_ensure_grayscale_converts_bgr(bgr_image):
    result = ensure_grayscale(bgr_image)
    assert result.ndim == 2
    assert result.shape == (100, 100)


def test_ensure_grayscale_raises_on_bad_shape():
    bad_image = np.zeros((100, 100, 4), dtype=np.uint8)
    with pytest.raises(ThalianaCVError):
        ensure_grayscale(bad_image)


# ---------------------------------------------------------------------------
# get_binary_mask
# ---------------------------------------------------------------------------


def test_get_binary_mask_returns_tuple(grayscale_image):
    threshold, mask = get_binary_mask(grayscale_image)
    assert isinstance(threshold, float)
    assert isinstance(mask, np.ndarray)


def test_get_binary_mask_values_are_binary(grayscale_image):
    _, mask = get_binary_mask(grayscale_image)
    unique_values = set(np.unique(mask))
    assert unique_values.issubset({0, 255})


def test_get_binary_mask_shape_matches_input(grayscale_image):
    _, mask = get_binary_mask(grayscale_image)
    assert mask.shape == grayscale_image.shape


# ---------------------------------------------------------------------------
# get_bounding_box
# ---------------------------------------------------------------------------


def test_get_bounding_box_returns_two_tuples(grayscale_image):
    _, binary = get_binary_mask(grayscale_image)
    bbox = get_bounding_box(binary)
    assert len(bbox) == 2
    assert len(bbox[0]) == 2
    assert len(bbox[1]) == 2


def test_get_bounding_box_is_square(grayscale_image):
    _, binary = get_binary_mask(grayscale_image)
    (x1, y1), (x2, y2) = get_bounding_box(binary)
    assert (x2 - x1) == (y2 - y1)


def test_get_bounding_box_raises_on_empty_mask():
    empty_mask = np.zeros((100, 100), dtype=np.uint8)
    with pytest.raises(ThalianaCVError):
        get_bounding_box(empty_mask)


def test_get_bounding_box_coords_within_image(grayscale_image):
    _, binary = get_binary_mask(grayscale_image)
    (x1, y1), (x2, y2) = get_bounding_box(binary)
    h, w = grayscale_image.shape
    assert x1 >= 0 and y1 >= 0
    assert x2 <= w and y2 <= h


# ---------------------------------------------------------------------------
# Synthetic -- size variation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "height,width,radius",
    [
        (512, 512, 200),
        (1024, 1024, 400),
        (2048, 2048, 800),
    ],
)
def test_detect_roi_square_images(height, width, radius):
    image = make_synthetic_image(height, width, radius)
    (x1, y1), (x2, y2) = detect_roi(image)
    assert (x2 - x1) == (y2 - y1)
    assert x1 >= 0 and y1 >= 0
    assert x2 <= width and y2 <= height


@pytest.mark.parametrize(
    "height,width,radius",
    [
        (3000, 4200, 1400),
        (2999, 4100, 1350),
        (3006, 4250, 1450),
    ],
)
def test_detect_roi_hades_like_dimensions(height, width, radius):
    """Synthetic images at HADES-like dimensions (4100-4250 x 2999-3006)."""
    image = make_synthetic_image(height, width, radius)
    (x1, y1), (x2, y2) = detect_roi(image)
    assert (x2 - x1) == (y2 - y1)
    assert x2 <= width and y2 <= height


@pytest.mark.parametrize(
    "cx,cy",
    [
        (1400, 1000),
        (2000, 1500),
        (2800, 1000),
    ],
)
def test_detect_roi_off_centre(cx, cy):
    """ROI at different positions within a HADES-like image."""
    image = make_synthetic_image(3000, 4200, 1200, center=(cx, cy))
    (x1, y1), (x2, y2) = detect_roi(image)
    assert (x2 - x1) == (y2 - y1)
    assert x1 >= 0 and y1 >= 0
    assert x2 <= 4200 and y2 <= 3000


# ---------------------------------------------------------------------------
# crop_to_roi
# ---------------------------------------------------------------------------


def test_crop_to_roi_reduces_size(grayscale_image):
    roi_bbox = detect_roi(grayscale_image)
    cropped = crop_to_roi(grayscale_image, roi_bbox)
    assert cropped.shape[0] <= grayscale_image.shape[0]
    assert cropped.shape[1] <= grayscale_image.shape[1]


def test_crop_to_roi_is_square(grayscale_image):
    roi_bbox = detect_roi(grayscale_image)
    cropped = crop_to_roi(grayscale_image, roi_bbox)
    assert cropped.shape[0] == cropped.shape[1]


def test_crop_to_roi_is_not_empty(grayscale_image):
    roi_bbox = detect_roi(grayscale_image)
    cropped = crop_to_roi(grayscale_image, roi_bbox)
    assert np.any(cropped > 0)


# ---------------------------------------------------------------------------
# Real HADES fixture tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("image_path", FIXTURE_IMAGES)
def test_detect_roi_real_image_returns_bbox(image_path):
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert image is not None, f"Could not load {image_path}"
    bbox = detect_roi(image)
    assert len(bbox) == 2


@pytest.mark.parametrize("image_path", FIXTURE_IMAGES)
def test_detect_roi_real_image_is_square(image_path):
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    (x1, y1), (x2, y2) = detect_roi(image)
    assert (x2 - x1) == (y2 - y1)


@pytest.mark.parametrize("image_path", FIXTURE_IMAGES)
def test_detect_roi_real_image_within_bounds(image_path):
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    h, w = image.shape
    (x1, y1), (x2, y2) = detect_roi(image)
    assert x1 >= 0 and y1 >= 0
    assert x2 <= w and y2 <= h


@pytest.mark.parametrize("image_path", FIXTURE_IMAGES)
def test_detect_roi_real_image_size_reasonable(image_path):
    """ROI should be close to the short image dimension (~3000px)."""
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    (x1, y1), (x2, y2) = detect_roi(image)
    roi_size = x2 - x1
    assert (
        2000 <= roi_size <= image.shape[0]
    ), f"ROI size {roi_size} outside expected range for {image_path.name}"


@pytest.mark.parametrize("image_path", FIXTURE_IMAGES)
def test_crop_to_roi_real_image_is_square(image_path):
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    roi_bbox = detect_roi(image)
    cropped = crop_to_roi(image, roi_bbox)
    assert cropped.shape[0] == cropped.shape[1]


@pytest.mark.parametrize("image_path", FIXTURE_IMAGES)
def test_crop_to_roi_real_image_is_not_empty(image_path):
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    roi_bbox = detect_roi(image)
    cropped = crop_to_roi(image, roi_bbox)
    assert np.any(cropped > 0)


# ---------------------------------------------------------------------------
# TODO tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "image_path",
    [
        FIXTURES_DIR / "test_image_05.png",
        FIXTURES_DIR / "test_image_12.png",
    ],
)
def test_detect_roi_unaffected_by_scale_bar(image_path):
    """ROI bounding box should not extend into the scale bar region.

    test_image_05 and test_image_12 have a ~90px wide scale bar composed
    of light pixels at the right edge of the image. If detect_roi is working
    correctly, x2 should be well clear of the last 90 pixels.
    """
    scale_bar_width = 90
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert image is not None, f"Could not load {image_path}"
    _, w = image.shape
    (x1, y1), (x2, y2) = detect_roi(image)
    assert x2 < w - scale_bar_width, (
        f"ROI right edge {x2} extends into scale bar region "
        f"(image width {w}, scale bar starts at {w - scale_bar_width})"
    )
