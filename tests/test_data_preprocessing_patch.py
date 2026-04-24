# tests/test_data_preprocessing_patch.py
"""Unit tests for thalianacv.data.preprocessing -- patch functions."""

from pathlib import Path

import cv2
import numpy as np
import pytest

from thalianacv.data.preprocessing import (
    crop_to_roi,
    detect_roi,
    padder,
    restore_mask_to_original,
    unpadder,
)

# ---------------------------------------------------------------------------
# padder
# ---------------------------------------------------------------------------


def test_padder_already_divisible():
    image = np.zeros((256, 256), dtype=np.uint8)
    result = padder(image, patch_size=256)
    assert result.shape == (256, 256)


def test_padder_makes_height_divisible():
    image = np.zeros((300, 256), dtype=np.uint8)
    result = padder(image, patch_size=256)
    assert result.shape[0] % 256 == 0


def test_padder_makes_width_divisible():
    image = np.zeros((256, 300), dtype=np.uint8)
    result = padder(image, patch_size=256)
    assert result.shape[1] % 256 == 0


def test_padder_both_dimensions():
    image = np.zeros((300, 300), dtype=np.uint8)
    result = padder(image, patch_size=256)
    assert result.shape[0] % 256 == 0
    assert result.shape[1] % 256 == 0


def test_padder_preserves_content():
    image = np.ones((300, 300), dtype=np.uint8) * 128
    result = padder(image, patch_size=256)
    assert np.any(result == 128)


def test_padder_pads_with_zeros():
    image = np.ones((300, 300), dtype=np.uint8) * 128
    result = padder(image, patch_size=256)
    assert result[0, 0] == 0


def test_padder_3channel_image():
    image = np.zeros((300, 300, 3), dtype=np.uint8)
    result = padder(image, patch_size=256)
    assert result.shape[0] % 256 == 0
    assert result.shape[1] % 256 == 0
    assert result.shape[2] == 3


@pytest.mark.parametrize(
    "h,w,patch_size",
    [
        (512, 512, 256),
        (1000, 1000, 256),
        (2999, 2999, 256),
        (300, 400, 128),
    ],
)
def test_padder_parametrized(h, w, patch_size):
    image = np.zeros((h, w), dtype=np.uint8)
    result = padder(image, patch_size=patch_size)
    assert result.shape[0] % patch_size == 0
    assert result.shape[1] % patch_size == 0


# ---------------------------------------------------------------------------
# unpadder
# ---------------------------------------------------------------------------


def test_unpadder_restores_roi_size():
    roi_bbox = ((10, 10), (310, 310))
    roi_h = 310 - 10
    roi_w = 310 - 10
    padded = np.zeros((512, 512), dtype=np.uint8)
    result = unpadder(padded, roi_bbox)
    assert result.shape == (roi_h, roi_w)


def test_unpadder_no_padding_needed():
    roi_bbox = ((0, 0), (256, 256))
    image = np.zeros((256, 256), dtype=np.uint8)
    result = unpadder(image, roi_bbox)
    assert result.shape == (256, 256)


def test_unpadder_3channel():
    roi_bbox = ((0, 0), (300, 300))
    padded = np.zeros((512, 512, 3), dtype=np.uint8)
    result = unpadder(padded, roi_bbox)
    assert result.ndim == 3
    assert result.shape[:2] == (300, 300)


# ---------------------------------------------------------------------------
# restore_mask_to_original
# ---------------------------------------------------------------------------


def test_restore_mask_shape_matches_original():
    original_shape = (1000, 1000)
    roi_bbox = ((100, 100), (600, 600))
    # roi_h = 600 - 100
    # roi_w = 600 - 100
    padded_mask = np.zeros((512, 512), dtype=np.uint8)
    padded_mask[100:200, 100:200] = 255
    result = restore_mask_to_original(padded_mask, original_shape, roi_bbox)
    assert result.shape == original_shape


def test_restore_mask_values_are_binary():
    original_shape = (1000, 1000)
    roi_bbox = ((100, 100), (600, 600))
    padded_mask = np.zeros((512, 512), dtype=np.uint8)
    padded_mask[100:200, 100:200] = 128
    result = restore_mask_to_original(padded_mask, original_shape, roi_bbox)
    unique = set(np.unique(result))
    assert unique.issubset({0, 255})


def test_restore_mask_outside_roi_is_zero():
    original_shape = (1000, 1000)
    roi_bbox = ((100, 100), (600, 600))
    padded_mask = np.ones((512, 512), dtype=np.uint8) * 255
    result = restore_mask_to_original(padded_mask, original_shape, roi_bbox)
    assert result[0, 0] == 0
    assert result[999, 999] == 0


def test_restore_mask_roi_region_is_nonzero():
    original_shape = (1000, 1000)
    roi_bbox = ((100, 100), (600, 600))
    padded_mask = np.ones((512, 512), dtype=np.uint8) * 255
    result = restore_mask_to_original(padded_mask, original_shape, roi_bbox)
    assert np.any(result[100:600, 100:600] > 0)


# ---------------------------------------------------------------------------
# Round-trip test
# ---------------------------------------------------------------------------


def test_padder_unpadder_roundtrip():
    """Pad then unpad should restore original dimensions."""
    original = np.zeros((300, 400), dtype=np.uint8)
    original[50:100, 50:100] = 255
    roi_bbox = ((0, 0), (400, 300))
    padded = padder(original, patch_size=256)
    restored = unpadder(padded, roi_bbox)
    assert restored.shape == original.shape


# ---------------------------------------------------------------------------
# Real HADES fixture tests
# ---------------------------------------------------------------------------


FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURE_IMAGES = [
    FIXTURES_DIR / "test_image_05.png",
    FIXTURES_DIR / "test_image_12.png",
    FIXTURES_DIR / "test_image_15.png",
]


@pytest.mark.parametrize("image_path", FIXTURE_IMAGES)
def test_padder_unpadder_roundtrip_real_image(image_path):
    """Pad then unpad a real HADES ROI should restore original dimensions."""
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert image is not None, f"Could not load {image_path}"
    roi_bbox = detect_roi(image)
    cropped = crop_to_roi(image, roi_bbox)
    padded = padder(cropped, patch_size=256)
    restored = unpadder(padded, roi_bbox)
    assert restored.shape == cropped.shape


@pytest.mark.parametrize("image_path", FIXTURE_IMAGES)
def test_restore_mask_content_preserved_real_image(image_path):
    """restore_mask_to_original should place mask content at the ROI location."""
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert image is not None, f"Could not load {image_path}"
    roi_bbox = detect_roi(image)
    cropped = crop_to_roi(image, roi_bbox)
    padded = padder(cropped, patch_size=256)
    full_mask = restore_mask_to_original(padded, image.shape, roi_bbox)
    (x1, y1), (x2, y2) = roi_bbox
    assert full_mask.shape == image.shape
    assert np.any(full_mask[y1:y2, x1:x2] > 0)
