# thalianacv/data/preprocessing.py
"""Image preprocessing functions for the thalianacv inference pipeline.

This module provides all image loading, ROI detection, patch extraction,
mask repair, and shoot mask cleaning functions required by the inference
pipeline. All functions operate on numpy arrays in memory. Optional
save_path arguments are provided where disk output is useful for debugging.

Functions are grouped into four sections:
    - ROI: detect and crop regions of interest
    - Patch: pad, unpatch, and restore images for patch-based inference
    - Mask repair: load and repair root segmentation masks
    - Shoot mask cleaning: clean and validate shoot segmentation masks

Dependencies:
    opencv-python, numpy, scipy, scikit-image
"""

from typing import Tuple

import cv2
import numpy as np

from thalianacv.utils.logging import ThalianaCVError, get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# ROI
# ---------------------------------------------------------------------------


def ensure_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert an image to grayscale if it is not already.

    Args:
        image: Input image array. Either a 2D grayscale image or a 3D
            BGR colour image with shape (H, W, 3).

    Returns:
        Grayscale image as a 2D numpy array.

    Raises:
        ThalianaCVError: If the image has an unexpected shape.

    Example:
        >>> gray = ensure_grayscale(cv2.imread("image.png"))
    """
    if len(image.shape) == 2:
        return image
    if len(image.shape) == 3 and image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    raise ThalianaCVError(f"Unexpected image shape: {image.shape}")


def get_binary_mask(
    image: np.ndarray,
    thresh: int = 128,
    maxval: int = 255,
) -> Tuple[float, np.ndarray]:
    """Create a binary mask using Otsu's thresholding.

    Args:
        image: Input image, colour or grayscale.
        thresh: Initial threshold value, ignored when using Otsu's method.
            Default is 128.
        maxval: Value assigned to pixels above threshold. Default is 255.

    Returns:
        Tuple of (threshold_value, binary_mask) where threshold_value is
        the computed Otsu threshold and binary_mask is a uint8 array with
        values in {0, maxval}.

    Example:
        >>> threshold, mask = get_binary_mask(image)
    """
    gray = ensure_grayscale(image)
    threshold, binary_mask = cv2.threshold(
        gray,
        thresh=thresh,
        maxval=maxval,
        type=cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )
    return threshold, binary_mask


def get_bounding_box(
    binary_mask: np.ndarray,
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Compute a square bounding box around the largest contour in a mask.

    Args:
        binary_mask: 2D binary image (uint8) where foreground pixels are
            non-zero.

    Returns:
        Tuple of ((x1, y1), (x2, y2)) giving the top-left and bottom-right
        coordinates of a square bounding box. Coordinates are clamped to
        image boundaries.

    Raises:
        ThalianaCVError: If no contours are found in the mask.

    Example:
        >>> bbox = get_bounding_box(binary_mask)
        >>> (x1, y1), (x2, y2) = bbox
    """
    contours, _ = cv2.findContours(
        binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        raise ThalianaCVError("No contours found in binary mask")

    max_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(max_contour)

    size = max(w, h)
    center_x = x + w // 2
    center_y = y + h // 2
    new_x = center_x - size // 2
    new_y = center_y - size // 2

    new_x = max(0, min(new_x, binary_mask.shape[1] - size))
    new_y = max(0, min(new_y, binary_mask.shape[0] - size))

    return (new_x, new_y), (new_x + size, new_y + size)


def detect_roi(
    image: np.ndarray,
) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Detect the ROI bounding box in an image.

    Detects the region of interest (e.g. petri dish) by thresholding and
    finding the largest contour.

    Args:
        image: Input image, BGR colour or grayscale.

    Returns:
        ROI bounding box as ((x1, y1), (x2, y2)).

    Example:
        >>> roi = detect_roi(image)
        >>> (x1, y1), (x2, y2) = roi
    """
    logger.debug("Detecting ROI")
    _, binary_mask = get_binary_mask(image)
    return get_bounding_box(binary_mask)


def crop_to_roi(
    image: np.ndarray,
    roi_bbox: Tuple[Tuple[int, int], Tuple[int, int]],
) -> np.ndarray:
    """Crop an image to its ROI bounding box.

    Args:
        image: Input image, colour or grayscale.
        roi_bbox: ((x1, y1), (x2, y2)) from detect_roi.

    Returns:
        Cropped image as numpy array.

    Example:
        >>> roi_bbox = detect_roi(image)
        >>> cropped = crop_to_roi(image, roi_bbox)
    """
    (x1, y1), (x2, y2) = roi_bbox
    return image[y1:y2, x1:x2]


# ---------------------------------------------------------------------------
# Patch
# ---------------------------------------------------------------------------


def padder(image: np.ndarray, patch_size: int) -> np.ndarray:
    """Pad an image so its dimensions are divisible by patch_size.

    Padding is applied evenly to both sides of each dimension using black
    (zero) pixels. If the padding amount is odd, one extra pixel is added
    to the bottom or right side.

    Args:
        image: Input image as numpy array with shape (H, W) or (H, W, C).
        patch_size: Target patch size. Both dimensions will be padded to
            the next multiple of this value.

    Returns:
        Padded image with dimensions divisible by patch_size.

    Example:
        >>> padded = padder(image, patch_size=256)
        >>> assert padded.shape[0] % 256 == 0
        >>> assert padded.shape[1] % 256 == 0
    """
    h, w = image.shape[:2]

    height_padding = (
        0 if h % patch_size == 0 else ((h // patch_size) + 1) * patch_size - h
    )
    width_padding = (
        0 if w % patch_size == 0 else ((w // patch_size) + 1) * patch_size - w
    )

    if height_padding == 0 and width_padding == 0:
        return image

    top = height_padding // 2
    bottom = height_padding - top
    left = width_padding // 2
    right = width_padding - left

    return cv2.copyMakeBorder(
        image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=0
    )


def unpadder(
    padded_image: np.ndarray,
    roi_bbox: Tuple[Tuple[int, int], Tuple[int, int]],
) -> np.ndarray:
    """Remove padding from an image to restore original ROI dimensions.

    Reverses the padding applied by padder() by calculating and removing
    the padding from all sides.

    Args:
        padded_image: Padded image as numpy array with shape (H, W) or
            (H, W, C).
        roi_bbox: ((x1, y1), (x2, y2)) representing the original ROI
            coordinates before padding was applied.

    Returns:
        Cropped image with original ROI dimensions.

    Example:
        >>> roi_bbox = detect_roi(image)
        >>> padded = padder(cropped, patch_size=256)
        >>> restored = unpadder(padded, roi_bbox)
    """
    h, w = padded_image.shape[:2]

    roi_height = roi_bbox[1][1] - roi_bbox[0][1]
    roi_width = roi_bbox[1][0] - roi_bbox[0][0]

    total_h_pad = h - roi_height
    total_w_pad = w - roi_width

    if total_h_pad == 0 and total_w_pad == 0:
        return padded_image

    left = total_w_pad // 2
    right = total_w_pad - left
    top = total_h_pad // 2
    bottom = total_h_pad - top

    if padded_image.ndim == 2:
        return padded_image[top:-bottom, left:-right]
    return padded_image[top:-bottom, left:-right, :]


def restore_mask_to_original(
    padded_mask: np.ndarray,
    original_shape: Tuple[int, ...],
    roi_bbox: Tuple[Tuple[int, int], Tuple[int, int]],
) -> np.ndarray:
    """Restore a padded mask to match the original image dimensions.

    Removes padding from the mask and places it at the correct position
    in a full-size mask matching the original image dimensions.

    Args:
        padded_mask: Padded binary mask as numpy array with shape (H, W).
        original_shape: Shape of the original image as (H, W) or
            (H, W, C).
        roi_bbox: ((x1, y1), (x2, y2)) representing the original ROI
            coordinates.

    Returns:
        Binary mask as numpy array with shape matching original_shape[:2],
        with values 0 and 255.

    Example:
        >>> full_mask = restore_mask_to_original(
        ...     predicted_mask, original_image.shape, roi_bbox
        ... )
    """
    unpadded = unpadder(padded_mask, roi_bbox)
    binary = (unpadded > 0).astype(np.uint8) * 255

    full_mask = np.zeros(original_shape[:2], dtype=np.uint8)
    (x1, y1), (x2, y2) = roi_bbox
    full_mask[y1:y2, x1:x2] = binary

    return full_mask
