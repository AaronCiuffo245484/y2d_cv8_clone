# thalianacv — Package Plan

## Overview

`thalianacv` is a production-ready Python package for plant image analysis, targeting the HADES phenotyping system at NPEC. It accepts plant images as input and returns segmentation masks, landmark locations, and confidence scores. The package exposes a CLI for local use and an API for remote/cloud inference.

---

## Top-Level Package Structure

```text
thalianacv/
├── src/
│   └── thalianacv/
│       ├── __init__.py
│       ├── core/
│       ├── data/
│       ├── database/
│       ├── models/
│       ├── api/
│       ├── cli/
│       └── utils/
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

The `src/` layout is used to prevent the package from being importable directly from the
project root during development, which ensures tests always exercise the installed package
rather than the working directory. This is the recommended layout for packages intended
for PyPI distribution.

---

## Submodules

### `thalianacv.core`

**Responsibility**: Orchestrates the inference pipeline. Acts as the main entry point for prediction logic, coordinating data loading, preprocessing, model inference, and postprocessing.

**Public interface**:

- `predict(image_path: str | Path) -> PredictionResult` — runs the full inference pipeline on a single image
- `batch_predict(image_dir: str | Path) -> list[PredictionResult]` — runs inference on a directory of images
- `PredictionResult` — dataclass containing segmentation masks, landmark coordinates, and confidence scores

**Depends on**: `thalianacv.data`, `thalianacv.models`, `thalianacv.utils`

---

### `thalianacv.data`

**Responsibility**: Handles all data loading, validation, and preprocessing. Converts raw images into the tensor format expected by the models. Also handles postprocessing of raw model outputs back into interpretable results.

**Public interface**:

- `load_image(path: str | Path) -> np.ndarray` — loads and validates an image
- `preprocess(image: np.ndarray) -> torch.Tensor` — resizes, normalises, and converts an image to a model-ready tensor
- `postprocess_masks(raw_output: torch.Tensor) -> np.ndarray` — converts raw segmentation output to a binary mask
- `postprocess_landmarks(raw_output: torch.Tensor) -> list[tuple[float, float]]` — converts raw landmark output to (x, y) coordinate pairs with confidence scores

**Depends on**: `thalianacv.utils`

---

### `thalianacv.models`

**Responsibility**: Loads, manages, and runs model inference. Abstracts over model architecture so that the rest of the package does not need to know which specific model is in use. Handles model weight loading and device management (CPU/GPU).

**Public interface**:

- `load_model(model_name: str, weights_path: str | Path) -> BaseModel` — loads a registered model by name with the given weights
- `list_models() -> list[str]` — returns names of all registered model architectures
- `BaseModel` — abstract base class that all model implementations must follow, exposing a `forward(tensor: torch.Tensor) -> dict` method

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

**Responsibility**: FastAPI application exposing the inference pipeline as an HTTP service. Handles request validation, authentication, and response serialisation. Intended to run inside a Docker container.

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

**Depends on**: `thalianacv.core`, `thalianacv.database`, `thalianacv.utils`

---

### `thalianacv.cli`

**Responsibility**: Typer-based CLI for local use. Wraps the core inference pipeline so that users can run predictions from the command line without writing Python code. Also exposes commands for model management.

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

- `get_logger(name: str) -> logging.Logger` — returns a consistently configured logger
- `load_config(path: str | Path) -> dict` — loads a YAML config file
- `ThalianaCVError` — base exception class for the package
- `PredictionResult` — shared dataclass for prediction outputs (imported by `core` and re-exported)

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

| Package | Purpose |
|---------|---------|
| `numpy` | Array operations and mask handling |
| `Pillow` | Image format support |
| `torch` | Model inference |
| `torchvision` | Pretrained model backbones and transforms |
| `fastapi` | API framework |
| `uvicorn` | ASGI server for running FastAPI |
| `python-multipart` | File upload support for FastAPI |
| `typer` | CLI framework |
| `pydantic` | Request/response validation in the API |
| `psycopg2-binary` | PostgreSQL driver |
| `sqlalchemy` | ORM for database interactions |
| `PyYAML` | Configuration file loading |
| `pytest` | Unit testing |
| `pytest-cov` | Coverage reporting |
| `ruff` | Linting and formatting |
| `sphinx` | Documentation generation |
| `pre-commit` | Git hook management |

---

## Notes

- This plan covers the MVP scope (Sprint 2). Submodules for training pipelines, monitoring,
  and retraining will be added in later sprints and this document will be updated accordingly.
- Model architecture implementations live inside `thalianacv.models` as submodules
  (e.g., `thalianacv.models.segmentation`, `thalianacv.models.landmark`). These are not
  defined here yet as the specific architectures carried over from Block B are still being decided.
- The frontend technology stack is marked for review and must be confirmed before Sprint 2 begins.

<!-- version 2 260420.1503 -->
