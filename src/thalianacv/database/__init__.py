# thalianacv/database/__init__.py
"""Public interface for the thalianacv database submodule.

Imports and re-exports all public database functions from
thalianacv.database.models so that callers can use the shorter import path:

    from thalianacv.database import save_submission, save_prediction

rather than importing from the models module directly.
"""

from thalianacv.database.models import (
    get_corrections,
    get_submissions,
    save_correction,
    save_prediction,
    save_submission,
)

__all__ = [
    "get_corrections",
    "get_submissions",
    "save_correction",
    "save_prediction",
    "save_submission",
]
