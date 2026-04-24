# tests/smoke/test_preprocess.py
"""Smoke test for thalianacv.data.preprocessing.

Runs the preprocessing pipeline on real HADES fixture images and produces
visual output for manual verification. Not run as part of the automated
test suite (prefixed with underscore).

Usage:
    # Show images interactively (requires display)
    poetry run python tests/_test_preprocess.py

    # Save images to disk instead of showing
    poetry run python tests/_test_preprocess.py --save

    # Configure patch size and step size
    poetry run python tests/_test_preprocess.py --patch-size 128 --step-size 64 --save

Output (when --save is used):
    tests/smoke_output/
        <image_name>_01_original.png
        <image_name>_02_roi_overlay.png
        <image_name>_03_cropped.png
        <image_name>_04_padded_grid.png
        <image_name>_05_restored.png
"""

import argparse
from pathlib import Path

import cv2
import numpy as np

from thalianacv.data.preprocessing import (
    crop_to_roi,
    detect_roi,
    padder,
    restore_mask_to_original,
    unpadder,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SMOKE_OUTPUT_DIR = Path(__file__).parent.parent / "smoke_output"

FIXTURE_IMAGES = [
    FIXTURES_DIR / "test_image_05.png",
    FIXTURES_DIR / "test_image_12.png",
]


def draw_roi_overlay(image: np.ndarray, roi_bbox) -> np.ndarray:
    """Draw ROI bounding box on a copy of the image.

    Args:
        image: Grayscale image as numpy array.
        roi_bbox: ((x1, y1), (x2, y2)) from detect_roi.

    Returns:
        BGR image with ROI rectangle drawn in green.
    """
    overlay = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    (x1, y1), (x2, y2) = roi_bbox
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 8)
    cv2.putText(
        overlay,
        f"ROI: ({x1},{y1}) -> ({x2},{y2})",
        (x1 + 20, y1 + 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        2.0,
        (0, 255, 0),
        4,
    )
    return overlay


def draw_patch_grid(
    image: np.ndarray,
    patch_size: int,
    step_size: int,
) -> np.ndarray:
    """Draw patch grid on a copy of the image.

    Draws patch boundaries in green and highlights overlap regions
    in yellow. Overlap exists wherever step_size < patch_size.

    Args:
        image: Grayscale image as numpy array (should be padded).
        patch_size: Size of each square patch in pixels.
        step_size: Step size between patches in pixels.

    Returns:
        BGR image with patch grid and overlap regions drawn.
    """
    h, w = image.shape[:2]
    overlay = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    overlap = patch_size - step_size

    # Highlight overlap regions in yellow if overlap exists
    if overlap > 0:
        col = 0
        while col + patch_size <= w:
            next_col = col + step_size
            if next_col + patch_size <= w:
                # Vertical overlap band
                cv2.rectangle(
                    overlay,
                    (next_col, 0),
                    (next_col + overlap, h),
                    (0, 200, 200),
                    -1,
                )
            col += step_size

        row = 0
        while row + patch_size <= h:
            next_row = row + step_size
            if next_row + patch_size <= h:
                # Horizontal overlap band
                cv2.rectangle(
                    overlay,
                    (0, next_row),
                    (w, next_row + overlap),
                    (0, 200, 200),
                    -1,
                )
            row += step_size

    # Draw patch boundaries in green
    col = 0
    while col + patch_size <= w:
        cv2.line(overlay, (col, 0), (col, h), (0, 255, 0), 2)
        col += step_size
    cv2.line(overlay, (w - 1, 0), (w - 1, h), (0, 255, 0), 2)

    row = 0
    while row + patch_size <= h:
        cv2.line(overlay, (0, row), (w, row), (0, 255, 0), 2)
        row += step_size
    cv2.line(overlay, (0, h - 1), (w, h - 1), (0, 255, 0), 2)

    n_cols = (w - patch_size) // step_size + 1
    n_rows = (h - patch_size) // step_size + 1
    cv2.putText(
        overlay,
        f"Patches: {n_rows}x{n_cols} | size={patch_size} step={step_size} overlap={overlap}",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (255, 255, 255),
        3,
    )
    return overlay


def draw_restored_overlay(
    original: np.ndarray,
    roi_bbox,
    restored_mask: np.ndarray,
) -> np.ndarray:
    """Overlay restored mask on original image.

    Args:
        original: Original grayscale image.
        roi_bbox: ((x1, y1), (x2, y2)) from detect_roi.
        restored_mask: Full-size mask from restore_mask_to_original.

    Returns:
        BGR image with mask overlaid in green and ROI boundary in red.
    """
    overlay = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    overlay[restored_mask > 0] = (0, 200, 0)
    (x1, y1), (x2, y2) = roi_bbox
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), 6)
    return overlay


def show_or_save(image: np.ndarray, title: str, path: Path, save: bool) -> None:
    """Show an image interactively or save it to disk.

    Args:
        image: BGR or grayscale image to display or save.
        title: Window title (used when showing interactively).
        path: Output path for saving.
        save: If True, save to disk. If False, show interactively.
    """
    if save:
        path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(path), image)
        print(f"  Saved: {path}")
    else:
        cv2.imshow(title, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def run_smoke_test(
    image_path: Path,
    patch_size: int,
    step_size: int,
    save: bool,
) -> None:
    """Run full preprocessing smoke test on a single image.

    Args:
        image_path: Path to the input HADES image.
        patch_size: Patch size for grid visualisation.
        step_size: Step size for grid visualisation.
        save: If True, save outputs to disk. If False, show interactively.
    """
    name = image_path.stem
    print(f"\nProcessing: {image_path.name}")

    # Step 1: Load original
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert image is not None, f"Could not load {image_path}"
    print(f"  Original shape: {image.shape}")
    show_or_save(
        image,
        f"{name} - 01 Original",
        SMOKE_OUTPUT_DIR / f"{name}_01_original.png",
        save,
    )

    # Step 2: Detect ROI and draw overlay
    roi_bbox = detect_roi(image)
    (x1, y1), (x2, y2) = roi_bbox
    print(f"  ROI: ({x1},{y1}) -> ({x2},{y2}), size={x2-x1}x{y2-y1}px")
    roi_overlay = draw_roi_overlay(image, roi_bbox)
    show_or_save(
        roi_overlay,
        f"{name} - 02 ROI Overlay",
        SMOKE_OUTPUT_DIR / f"{name}_02_roi_overlay.png",
        save,
    )

    # Step 3: Crop to ROI
    cropped = crop_to_roi(image, roi_bbox)
    print(f"  Cropped shape: {cropped.shape}")
    show_or_save(
        cropped,
        f"{name} - 03 Cropped ROI",
        SMOKE_OUTPUT_DIR / f"{name}_03_cropped.png",
        save,
    )

    # Step 4: Pad and draw patch grid
    padded = padder(cropped, patch_size=patch_size)
    print(f"  Padded shape: {padded.shape}")
    n_cols = (padded.shape[1] - patch_size) // step_size + 1
    n_rows = (padded.shape[0] - patch_size) // step_size + 1
    print(f"  Patch grid: {n_rows}x{n_cols} patches")
    patch_grid = draw_patch_grid(padded, patch_size, step_size)
    show_or_save(
        patch_grid,
        f"{name} - 04 Patch Grid",
        SMOKE_OUTPUT_DIR / f"{name}_04_padded_grid.png",
        save,
    )

    # Step 5: Simulate a mask (use padded image content as stand-in)
    # In real inference this would be the model output.
    # Here we threshold the padded image to simulate a binary mask.
    _, simulated_mask = cv2.threshold(
        padded, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    restored = restore_mask_to_original(simulated_mask, image.shape, roi_bbox)
    print(f"  Restored mask shape: {restored.shape}")
    restored_overlay = draw_restored_overlay(image, roi_bbox, restored)
    show_or_save(
        restored_overlay,
        f"{name} - 05 Restored Mask Overlay",
        SMOKE_OUTPUT_DIR / f"{name}_05_restored.png",
        save,
    )

    print(f"  Done: {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Smoke test for thalianacv.data.preprocessing"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output images to tests/smoke_output/ instead of showing interactively",
    )
    parser.add_argument(
        "--patch-size",
        type=int,
        default=256,
        help="Patch size in pixels (default: 256)",
    )
    parser.add_argument(
        "--step-size",
        type=int,
        default=128,
        help="Step size in pixels (default: 128)",
    )
    args = parser.parse_args()

    print(f"Patch size: {args.patch_size}, Step size: {args.step_size}")
    print(f"Overlap: {args.patch_size - args.step_size}px")
    print(f"Output mode: {'save to disk' if args.save else 'show interactively'}")

    for image_path in FIXTURE_IMAGES:
        if not image_path.exists():
            print(f"WARNING: fixture not found, skipping: {image_path}")
            continue
        run_smoke_test(image_path, args.patch_size, args.step_size, args.save)

    if args.save:
        print(f"\nAll outputs saved to: {SMOKE_OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
