# thalianacv/utils/types.py
"""Shared type definitions for thalianacv.

This module defines the core data structures used across the package.
All submodules that produce or consume prediction results should import
from here rather than defining their own types.

Note:
    PredictionResult is an internal dataclass, not a Pydantic model.
    To serialise it for an HTTP response, define a Pydantic response model
    in thalianacv.api that mirrors these fields. When converting:

    - shoot_mask and root_mask are numpy arrays, convert with .tolist()
    - coordinates is a pandas DataFrame, convert with .to_dict("records")
    - confidence_score is a plain float and needs no conversion

    A Pydantic response model should be defined in thalianacv.api with
    fields shoot_mask, root_mask, coordinates, and confidence_score.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class PredictionResult:
    """Output of a single inference run on a plant image.

    This is the internal contract between thalianacv.core and all consumers
    (API, CLI, database). All fields are populated by predict() in
    thalianacv.core.predict.

    When predict() is running as a stub, fields contain sentinel values
    that are impossible in real output, making stubs easy to detect.
    shoot_mask and root_mask are arrays filled with -1, coordinates is a
    DataFrame with correct columns and all values set to -999.0, and
    confidence_score is -1.0.
    """

    shoot_mask: np.ndarray
    root_mask: np.ndarray
    coordinates: pd.DataFrame
    confidence_score: float

    @staticmethod
    def empty_coordinates() -> pd.DataFrame:
        """Return a stub coordinates DataFrame with sentinel values.

        Returns a valid DataFrame with the correct column structure and
        5 rows, all numeric values set to -999.0. Used by predict() stub
        and as a reference for the expected DataFrame schema.

        Returns:
            DataFrame with 5 rows and all expected coordinate columns.
        """
        columns = [
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
        data = {col: [-999.0] * 5 for col in columns}
        data["plant_order"] = [1, 2, 3, 4, 5]
        data["Plant ID"] = ["stub"] * 5
        return pd.DataFrame(data)
