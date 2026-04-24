# tests/test_core_predict.py
"""Unit tests for thalianacv.core.predict stub."""

import numpy as np
import pandas as pd
import pytest

from thalianacv.core.predict import predict
from thalianacv.utils.types import PredictionResult

# --- Return type ---


def test_predict_returns_prediction_result():
    result = predict(
        image_path="image.png",
        shoot_model_path="shoot.h5",
        root_model_path="root.h5",
    )
    assert isinstance(result, PredictionResult)


# --- Stub sentinel values ---


def test_predict_confidence_score_is_sentinel():
    result = predict(
        image_path="image.png",
        shoot_model_path="shoot.h5",
        root_model_path="root.h5",
    )
    assert result.confidence_score == -1.0


def test_predict_shoot_mask_is_sentinel():
    result = predict(
        image_path="image.png",
        shoot_model_path="shoot.h5",
        root_model_path="root.h5",
    )
    assert np.all(result.shoot_mask == -1)


def test_predict_root_mask_is_sentinel():
    result = predict(
        image_path="image.png",
        shoot_model_path="shoot.h5",
        root_model_path="root.h5",
    )
    assert np.all(result.root_mask == -1)


def test_predict_coordinates_is_dataframe():
    result = predict(
        image_path="image.png",
        shoot_model_path="shoot.h5",
        root_model_path="root.h5",
    )
    assert isinstance(result.coordinates, pd.DataFrame)


def test_predict_coordinates_has_five_rows():
    result = predict(
        image_path="image.png",
        shoot_model_path="shoot.h5",
        root_model_path="root.h5",
    )
    assert len(result.coordinates) == 5


def test_predict_coordinates_sentinel_values():
    result = predict(
        image_path="image.png",
        shoot_model_path="shoot.h5",
        root_model_path="root.h5",
    )
    assert all(result.coordinates["Length (px)"] == -999.0)


# --- global_stats_path argument ---


def test_predict_accepts_none_global_stats_path():
    result = predict(
        image_path="image.png",
        shoot_model_path="shoot.h5",
        root_model_path="root.h5",
        global_stats_path=None,
    )
    assert isinstance(result, PredictionResult)


def test_predict_accepts_explicit_global_stats_path():
    result = predict(
        image_path="image.png",
        shoot_model_path="shoot.h5",
        root_model_path="root.h5",
        global_stats_path="custom_stats.json",
    )
    assert isinstance(result, PredictionResult)


# --- TODO tests (need real model output) ---


@pytest.mark.skip(reason="TODO: needs real image and model fixtures")
def test_predict_shoot_mask_shape_matches_input():
    pass


@pytest.mark.skip(reason="TODO: needs real image and model fixtures")
def test_predict_root_mask_values_are_binary():
    pass


@pytest.mark.skip(reason="TODO: needs real image and model fixtures")
def test_predict_confidence_score_in_valid_range():
    pass


@pytest.mark.skip(reason="TODO: needs real image and model fixtures")
def test_predict_coordinates_plant_ids_match_image_name():
    pass


@pytest.mark.skip(reason="TODO: needs real image and model fixtures")
def test_predict_raises_on_missing_image():
    pass


@pytest.mark.skip(reason="TODO: needs real image and model fixtures")
def test_predict_raises_on_missing_model():
    pass
