# thalianacv — Package Plan

## Overview

`thalianacv` is a production-ready Python package for plant image analysis, targeting the HADES phenotyping system at NPEC. It accepts plant images as input and returns segmentation masks, landmark locations, and confidence scores. The package exposes a CLI for local use and an API for remote/cloud inference.


## Top-Level Package Structure

```text
thalianacv/
├── thalianacv/
│   ├── __init__.py
│   ├── core/
│   ├── data/
│   ├── database/
│   ├── models/
│   ├── api/
│   ├── cli/
│   └── utils/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```
The `src/` layout is used to prevent the package from being importable directly from the project root during development, which ensures tests always exercise the installed package rather than the working directory. This is the recommended layout  for packages intended for PyPI distribution.

## Submodules

### `thalianacv.core`

**Responsibility**: Orchestrates the inference pipeline. Acts as the main entry point for prediction logic, coordinating data loading, preprocessing,
model inference, and postprocessing.

**Public interface**:

- `predict(image_path: str | Path, shoot_model_path: str | Path, root_model_path: str | Path, global_stats_path: str | Path | None = None) -> PredictionResult` — runs the full inference pipeline on a single image. If `global_stats_path` is `None`, loads bundled default stats from `thalianacv/data/default_stats.json`.
- `batch_predict(image_dir: str | Path) -> list[PredictionResult]` — runs
  inference on a directory of images
- `PredictionResult` — dataclass containing segmentation masks, landmark
  coordinates, and confidence scores

**Depends on**: `thalianacv.data`, `thalianacv.models`, `thalianacv.utils`

---

### `thalianacv.data`

**Responsibility**: Handles all data operations across the inference pipeline.
Split into two files with distinct responsibilities:

`preprocessing.py` handles everything that happens before inference: image
loading, ROI detection, cropping, and patch padding. It converts raw images
into the format expected by the models.

`postprocessing.py` handles everything that happens after inference: repairing
root masks, cleaning shoot masks, and restoring masks to original image
dimensions. It converts raw model outputs into clean, usable masks.

**Public interface — `preprocessing.py`**:

- `load_image(path: str | Path) -> np.ndarray` — loads and validates an image
- `ensure_grayscale(image: np.ndarray) -> np.ndarray` — converts to grayscale
- `detect_roi(image: np.ndarray) -> tuple` — detects ROI bounding box
- `crop_to_roi(image: np.ndarray, roi_bbox: tuple) -> np.ndarray` — crops to ROI
- `padder(image: np.ndarray, patch_size: int) -> np.ndarray` — pads image for patch extraction
- `unpadder(image: np.ndarray, roi_bbox: tuple) -> np.ndarray` — removes padding
- `restore_mask_to_original(mask: np.ndarray, original_shape: tuple, roi_bbox: tuple) -> np.ndarray` — restores mask to original image dimensions

**Public interface — `postprocessing.py`**:

- `repair_root_mask(mask: np.ndarray, save_path: str | Path | None = None) -> np.ndarray` — repairs gaps in root segmentation masks produced by inference
- `clean_shoot_mask(mask: np.ndarray, global_stats: dict, save_path: str | Path | None = None) -> dict` — cleans and validates shoot segmentation masks produced by inference

**Depends on**: `thalianacv.utils`

---

### `thalianacv.models`

**Responsibility**: Loads, manages, and runs model inference. Contains a thin
wrapper over the Keras/TensorFlow model loading and inference pipeline. This
wrapper is explicitly temporary — it is designed to be replaced when the Azure
ML training pipeline is in place and model management moves to registered
model endpoints.

The wrapper must be replaced when: (1) models are registered via Azure ML and
loaded from a model registry rather than a file path, or (2) the model
architecture changes from Keras to another framework.

**Public interface**:

- `load_model(weights_path: str | Path) -> object` — loads a Keras segmentation model from a file path. Returns the loaded model object.
- `run_inference(model: object, image: np.ndarray, patch_size: int = 256, step_size: int = 128) -> tuple[np.ndarray, float]` — runs patch-based inference on a single image. Returns a tuple of (binary_mask, mean_confidence) where mean_confidence is the mean foreground probability across all patches.

**Depends on**: `thalianacv.utils`

---

### `thalianacv.database`

**Responsibility**: Handles all interactions with the PostgreSQL database. Stores and retrieves submission metadata, prediction results, and user corrections. Acts as the single point of contact for database operations across the package, so that no other submodule needs to know the details of the database schema.

**Public interface**:

- `save_submission(image_path: str | Path, user_id: str) -> int` — saves a new image submission and returns the generated submission ID
- `save_prediction(submission_id: int, result: PredictionResult) -> int` — saves prediction results linked to a submission and returns the prediction ID
- `save_correction(prediction_id: int, is_correct: bool, annotation: dict | None) -> None` — records user feedback on a prediction
- `get_submissions(user_id: str) -> list[dict]` — retrieves all submissions for a given user
- `get_corrections() -> list[dict]` — retrieves all flagged corrections, used by the retraining pipeline

**Depends on**: `thalianacv.utils`

---

### `thalianacv.api`

**Responsibility**: FastAPI application exposing the inference pipeline as an HTTP service. Handles request validation, authentication, and response
serialisation. Intended to run inside a Docker container.

**Public interface** (HTTP endpoints):

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Returns service status |
| `POST` | `/predict` | Accepts an image file, returns masks, landmarks, and confidence scores |
| `POST` | `/predict/batch` | Accepts a zip of images, returns predictions for each |
| `GET` | `/models` | Lists available registered models |
| `POST` | `/submissions` | Creates a new image submission record |
| `POST` | `/corrections` | Accepts a user correction on a prediction |
| `GET` | `/metrics` | Returns monitoring metrics for the dashboard |
| `GET` | `/docs` | Auto-generated Swagger UI (built into FastAPI) |

**Depends on**: `thalianacv.core`, `thalianacv.utils`

---

### `thalianacv.cli`

**Responsibility**: Typer-based CLI for local use. Wraps the core inference pipeline so that users can run predictions from the command line without
writing Python code. Also exposes commands for model management.

**Public interface** (CLI commands):

| Command | Description |
|---------|-------------|
| `thalianacv predict <image>` | Run inference on a single image |
| `thalianacv predict-batch <dir>` | Run inference on all images in a directory |
| `thalianacv models list` | List available registered models |
| `thalianacv models download <n>` | Download a model by name |
| `thalianacv --help` | Show help |

**Depends on**: `thalianacv.core`, `thalianacv.utils`

---

### `thalianacv.utils`

**Responsibility**: Shared utilities used across the package. Includes logging configuration, custom exception definitions, configuration file loading, and type definitions used across submodules.

**Public interface**:

- `get_logger(name: str) -> logging.Logger` — returns a consistently configured
  logger
- `load_config(path: str | Path) -> dict` — loads a YAML config file
- `ThalianaCVError` — base exception class for the package
- `PredictionResult` — shared dataclass for prediction outputs (imported by
  `core` and re-exported)

**Depends on**: nothing (no internal dependencies)
---

## Frontend

The frontend is a containerised web application served separately from the Python package.
It is located in the `frontend/` directory at the project root and has its own `Dockerfile`.
It communicates with the backend exclusively via the `thalianacv.api` HTTP endpoints.

**Technology**: To be confirmed by the team in Sprint 2. A lightweight JavaScript framework
(e.g., React, Vue, or plain HTML/JS served via Nginx) is recommended given the team's
familiarity and the scope of the UI.

**Pages and views**:

| View | Description |
|------|-------------|
| Submit | Upload a plant image and submit it for inference |
| Results | Display the returned segmentation mask overlay, root-tip coordinates, and confidence score for a prediction |
| Corrections | Allow a user to mark a prediction as incorrect and optionally upload an annotation file |
| History | List all submissions for the current session with links to their prediction results |
| Dashboard | Display operational and business monitoring metrics: prediction confidence trends, correction rates, retraining history, latency, and error rate |

**API dependencies**: The frontend depends on the following backend endpoints:

- `POST /predict` — submit an image and receive results
- `POST /submissions` — create a submission record
- `POST /corrections` — submit a user correction
- `GET /metrics` — fetch data for the monitoring dashboard
- `GET /health` — check backend availability on page load

**Deployment**: The frontend container is included in the `docker-compose.yml` stack alongside
the backend and PostgreSQL containers. In cloud deployment it is served as a containerised
Azure Web App or behind an Azure Application Gateway.

---

## Submodule Dependency Map

```text
utils  <-- (no internal deps)
  ^
  |
data  <-- utils
  ^
  |
database  <-- utils
  ^
  |
models  <-- utils
  ^
  |
core  <-- data, database, models, utils
  ^         ^
  |         |
api       cli
frontend  <-- api (HTTP only, no Python import dependency)

```

---

## Third-Party Dependencies

| Package            | Purpose                                |
| ------------------ | -------------------------------------- |
| `numpy`            | Array operations and mask handling     |
| `opencv-python`    | Image loading, ROI detection, morphological operations |
| `pandas`           | Coordinate output as DataFrame         |
| `tensorflow`       | Keras model loading and inference      |
| `patchify`         | Patch extraction for inference         |
| `scipy`            | Peak detection in shoot mask cleaning  |
| `scikit-image`     | Connected component analysis           |
| `fastapi`          | API framework                          |
| `uvicorn`          | ASGI server for running FastAPI        |
| `python-multipart` | File upload support for FastAPI        |
| `typer`            | CLI framework                          |
| `pydantic`         | Request/response validation in the API |
| `PyYAML`           | Configuration file loading             |
| `pytest`           | Unit testing                           |
| `sphinx`           | Documentation generation               |

---

## Global Stats and Confidence Baseline

### Purpose

Shoot mask quality validation in the inference pipeline relies on a set of global Y-pixel statistics (`global_mean`, `global_std`) computed from a reference batch of training images. These are used by `clean_shoot_mask` to detect degraded or anomalous shoot masks before proceeding to root-shoot matching.

### MVP Implementation

The default stats are stored as a JSON file bundled with the package at:

```text
thalianacv/data/default_stats.json
```

`predict()` loads this file automatically when `global_stats_path=None`. To use updated stats, pass a path to a replacement JSON file with the same schema.

### Update Pattern

When the retraining pipeline produces a new set of stats (e.g. after a batch of new images is processed), the result is written to a JSON file at a known location. The caller passes that path via `global_stats_path`. No code changes are required.

### Future Hook

As confidence drift monitoring is added in later sprints, the retraining system will be responsible for computing and persisting updated stats. The `global_stats_path` argument is the intended integration point. When mean confidence falls below a threshold, the pipeline triggers retraining and updates the stats file on completion.

---

## `PredictionResult` Fields

| Field | Type | Description |
|---|---|---|
| `shoot_mask` | `np.ndarray` | Binary shoot segmentation mask |
| `root_mask` | `np.ndarray` | Binary root segmentation mask |
| `coordinates` | `pd.DataFrame` | Per-plant coordinates and root lengths (5 rows) |
| `confidence_score` | `float` | Mean foreground prediction probability averaged across shoot and root masks |

---

## Refactoring Map (Sprint 2)

The following existing source files are refactored into the package structure. The originals in `library/` are retained until the package is verified working.

| Source file | Destination |
|---|---|
| `run_inference.py` | `thalianacv/models/inference.py` |
| `roi.py`, `patch_dataset.py` (inference functions only) | `thalianacv/data/preprocessing.py` |
| `mask_processing.py` | `thalianacv/data/postprocessing.py` |
| `shoot_mask_cleaning.py` (inference functions only) | `thalianacv/data/postprocessing.py` |
| `root_shoot_matching.py` | imported by `thalianacv/core/predict.py` |
| `root_analysis.py` | internal dependency, not refactored in Sprint 2 |

---

## Notes

- This plan covers the MVP scope (Sprint 2). Submodules for training pipelines,
  monitoring, and retraining will be added in later sprints and this document
  will be updated accordingly.
- The `thalianacv.models` wrapper over Keras is explicitly temporary. It must
  be replaced when models are managed via Azure ML registered endpoints.
- `calculate_global_y_stats` from `shoot_mask_cleaning.py` is not included in
  `postprocessing.py` as it is only needed during retraining, not inference.
  It will be added to the training pipeline submodule in Sprint 3.

---

Version 3 2026.04.23.1213