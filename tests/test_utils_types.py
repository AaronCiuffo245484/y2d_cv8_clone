# tests/test_utils_types.py
"""Unit tests for thalianacv.utils.types."""

import numpy as np
import pandas as pd
import pytest

from thalianacv.utils.types import PredictionResult

# --- PredictionResult construction ---


def test_prediction_result_instantiates():
    result = PredictionResult(
        shoot_mask=np.zeros((10, 10), dtype=np.int8),
        root_mask=np.zeros((10, 10), dtype=np.int8),
        coordinates=PredictionResult.empty_coordinates(),
        confidence_score=0.0,
    )
    assert isinstance(result, PredictionResult)


def test_prediction_result_fields_exist():
    result = PredictionResult(
        shoot_mask=np.zeros((10, 10), dtype=np.int8),
        root_mask=np.zeros((10, 10), dtype=np.int8),
        coordinates=PredictionResult.empty_coordinates(),
        confidence_score=0.5,
    )
    assert hasattr(result, "shoot_mask")
    assert hasattr(result, "root_mask")
    assert hasattr(result, "coordinates")
    assert hasattr(result, "confidence_score")


# --- empty_coordinates ---


def test_empty_coordinates_returns_dataframe():
    df = PredictionResult.empty_coordinates()
    assert isinstance(df, pd.DataFrame)


def test_empty_coordinates_has_five_rows():
    df = PredictionResult.empty_coordinates()
    assert len(df) == 5


def test_empty_coordinates_plant_order():
    df = PredictionResult.empty_coordinates()
    assert list(df["plant_order"]) == [1, 2, 3, 4, 5]


def test_empty_coordinates_sentinel_values():
    df = PredictionResult.empty_coordinates()
    numeric_cols = [
        "Length (px)",
        "top_node_x",
        "top_node_y",
        "endpoint_x",
        "endpoint_y",
        "top_node_robot_x",
        "top_node_robot_y",
        "top_node_robot_z",
        "endpoint_robot_x",
        "endpoint_robot_y",
        "endpoint_robot_z",
    ]
    for col in numeric_cols:
        assert all(df[col] == -999.0), f"Expected -999.0 in column {col}"


def test_empty_coordinates_has_required_columns():
    df = PredictionResult.empty_coordinates()
    required = [
        "plant_order",
        "Plant ID",
        "Length (px)",
        "length_px",
        "top_node_x",
        "top_node_y",
        "endpoint_x",
        "endpoint_y",
        "top_node_robot_x",
        "top_node_robot_y",
        "top_node_robot_z",
        "endpoint_robot_x",
        "endpoint_robot_y",
        "endpoint_robot_z",
    ]
    for col in required:
        assert col in df.columns, f"Missing column: {col}"


def test_empty_coordinates_plant_id_is_stub():
    df = PredictionResult.empty_coordinates()
    assert all(df["Plant ID"] == "stub")


# --- Stub sentinel detection ---


def test_confidence_score_sentinel():
    result = PredictionResult(
        shoot_mask=np.full((10, 10), -1, dtype=np.int8),
        root_mask=np.full((10, 10), -1, dtype=np.int8),
        coordinates=PredictionResult.empty_coordinates(),
        confidence_score=-1.0,
    )
    assert result.confidence_score == -1.0


def test_mask_sentinel_values():
    stub_mask = np.full((10, 10), -1, dtype=np.int8)
    result = PredictionResult(
        shoot_mask=stub_mask,
        root_mask=stub_mask.copy(),
        coordinates=PredictionResult.empty_coordinates(),
        confidence_score=-1.0,
    )
    assert np.all(result.shoot_mask == -1)
    assert np.all(result.root_mask == -1)


# --- TODO tests (need real model output) ---


@pytest.mark.skip(reason="TODO: populate with real model output fixture")
def test_shoot_mask_shape_matches_input_image():
    pass


@pytest.mark.skip(reason="TODO: populate with real model output fixture")
def test_root_mask_values_are_binary():
    pass


@pytest.mark.skip(reason="TODO: populate with real model output fixture")
def test_confidence_score_in_valid_range():
    pass


@pytest.mark.skip(reason="TODO: populate with real model output fixture")
def test_coordinates_plant_ids_match_image_name():
    pass
