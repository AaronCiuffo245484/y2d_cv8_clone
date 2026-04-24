# tests/test_database.py
"""Unit tests for thalianacv.database stubs."""

import numpy as np
import pytest

from thalianacv.database import (
    get_corrections,
    get_submissions,
    save_correction,
    save_prediction,
    save_submission,
)
from thalianacv.utils.types import PredictionResult


@pytest.fixture
def stub_result():
    """Return a stub PredictionResult with sentinel values."""
    return PredictionResult(
        shoot_mask=np.full((10, 10), -1, dtype=np.int8),
        root_mask=np.full((10, 10), -1, dtype=np.int8),
        coordinates=PredictionResult.empty_coordinates(),
        confidence_score=-1.0,
    )


# --- save_submission ---


def test_save_submission_returns_int():
    result = save_submission("image.png", "user_01")
    assert isinstance(result, int)


def test_save_submission_returns_sentinel():
    result = save_submission("image.png", "user_01")
    assert result == -1


# --- save_prediction ---


def test_save_prediction_returns_int(stub_result):
    result = save_prediction(1, stub_result)
    assert isinstance(result, int)


def test_save_prediction_returns_sentinel(stub_result):
    result = save_prediction(1, stub_result)
    assert result == -1


# --- save_correction ---


def test_save_correction_returns_none():
    result = save_correction(1, is_correct=False)
    assert result is None


def test_save_correction_accepts_annotation():
    result = save_correction(1, is_correct=False, annotation={"note": "root missed"})
    assert result is None


def test_save_correction_accepts_none_annotation():
    result = save_correction(1, is_correct=True, annotation=None)
    assert result is None


# --- get_submissions ---


def test_get_submissions_returns_list():
    result = get_submissions("user_01")
    assert isinstance(result, list)


def test_get_submissions_returns_empty():
    result = get_submissions("user_01")
    assert result == []


# --- get_corrections ---


def test_get_corrections_returns_list():
    result = get_corrections()
    assert isinstance(result, list)


def test_get_corrections_returns_empty():
    result = get_corrections()
    assert result == []


# --- TODO tests (need real database connection) ---


@pytest.mark.skip(reason="TODO: needs real database connection fixture")
def test_save_submission_persists_to_database():
    pass


@pytest.mark.skip(reason="TODO: needs real database connection fixture")
def test_save_prediction_links_to_submission():
    pass


@pytest.mark.skip(reason="TODO: needs real database connection fixture")
def test_get_submissions_returns_correct_user_records():
    pass


@pytest.mark.skip(reason="TODO: needs real database connection fixture")
def test_get_corrections_returns_all_flagged_records():
    pass
