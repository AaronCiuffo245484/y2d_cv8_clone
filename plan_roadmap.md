# Project Plan and Roadmap <!-- omit from toc -->

- **Project:** Plant Phenotyping CV Application — HADES / NPEC
- **Course:** ADS-AI Year 2, Block D
- **Team:** Group CV8
  - Andrii Rak 243703
  - Yuliia Medun  244775
  - Lars Peggeman  241863
  - Andrii Humeha  243801
  - Aaron Ciuffo  245484
- **Repository:** https://github.com/BredaUniversityADSAI/2025-26d-fai2-adsai-group-computervision8
- **Block Start:** 13 April 2026
- **Deadline:** 12 June 2026

- [Project Overview](#project-overview)
- [System Architecture Overview](#system-architecture-overview)
- [MoSCoW Feature Prioritization](#moscow-feature-prioritization)
- [Sprint Milestones and Deadlines](#sprint-milestones-and-deadlines)
- [Feature-to-Sprint Mapping](#feature-to-sprint-mapping)
- [Dependency Mapping](#dependency-mapping)
- [Team Responsibilities](#team-responsibilities)

## Project Overview

This project creates a production ready computer vision pipeline for automated plat phenotyping using the NPEC HADES imaging system. The system accepts plant images as input and returns segmentation masks, root-tip coordinates and per-prediction confidence scores. It is deployed locally via Docker and in the cloud via Microsoft Azure.

The system must support user-driven model improvement. Users can submit new images with annotations, trigger retraining, and review model performance over time through a monitoring dashboard. All submitted data is stored as files; a PostgresSQL database stores metadata and filenames. Files are stored on disk.

The application is built as a production grade Python package with a REST API backend, a containerised frontend and automated CI/CD pipelines on Azure.

## System Architecture Overview

The system consists of the following components:

**Inference API** - A FastAPI service that accepts image input, runs the segmentation and root-tip detection model and returns masks, coordinates and confidence scores.

**Training Pipeline** - An Azure ML pipeline that ingests data, preprocesses images, trains the model, evaluates against a threshold and conditionally registers the model.

**Data Pipeline** - An ingestion and preprocessing pipeline, triggered on a schedule by new data, on demand, or in response to model drift that prepares annotated images for training.

**PostgreSQL Database** - Stores submission metadata (filename, timestamp, user ID, prediction ID, correction status) and model performance metrics. Does not store raw image files.

**File Storage** - Azure file storage for raw images, annotation files, model weights and development files.

**Front End** - A web based UI using platform Flask through which users submit images, view predictions, provide corrections and inspect the monitoring dashboard.

**CI/CD Pipeline** - Github actions workflows for linting, testing, building Docker images and triggering deployments.

**Monitoring** - Operational metrics (latency, error rate, drift) tracked via Azure ML monitoring. Business metrics such as prediction confidence trends, correction rates and retraining history will be visualized in a frontend dashboard.

## MoSCoW Feature Prioritization

MoSCoW Categories Defined

- Must have (M): Non-negotiable, critical requirements without which the product fails to deliver value, violates safety regulations, or is not legal.
- Should have (S): Important, high-value features that are not time-critical, but should be included if possible, often deemed "essential but not vital".
- Could have (C): Desirable "nice-to-have" features that improve user experience but have minimal impact if left out, often included to maximize value within time constraints.
- Won't have (W): Features identified as lowest priority, not required for the current release cycle, or deferred to a later date (sometimes referred to as "wish list" items)

### Must Have

These features are required to meet the project requirements as per the brief and must-pass ILOs (9.3, 9.4, 9.5).

| ID  | Feature                                                                     | Justification                                        |Completed|
| --- | --------------------------------------------------------------------------- | ---------------------------------------------------- |---------|
| M01 | Segmentation mask output from model                                         | Core product output per domain brief                 |         |
| M02 | Root-tip coordinate output from model                                       | Core product output per domain brief                 |         |
| M03 | Per-prediction confidence scores                                            | Required by domain brief                             |         |
| M04 | Production-ready Python package (installable via pip, with wheel and sdist) | Required by General Project Requirements and ILO 9.3 |         |
| M05 | CLI for inference and training                                              | Required by General Project Requirements and ILO 9.3 |         |
| M06 | Docstrings and Sphinx documentation                                         | Required by ILO 9.3                                  |         |
| M07 | Unit tests with coverage reporting                                          | Required by ILO 9.3                                  |         |
| M08 | Logging and error handling throughout codebase                              | Required by ILO 9.3                                  |         |
| M09 | FastAPI inference endpoint                                                  | Required by General Project Requirements and ILO 9.5 |         |
| M10 | Docker containers for backend, frontend, and database                       | Required by General Project Requirements and ILO 9.5 |         |
| M11 | Local deployment via Docker Compose                                         | Required by project deliverables                     |         |
| M12 | On-premise deployment via Portainer                                         | Required by project deliverables                     |         |
| M13 | Azure ML workspace with registered models, data assets, and environments    | Required by project deliverables and ILO 9.4         |         |
| M14 | Cloud data storage with versioned data assets in Azure Blob Storage         | Required by ILO 9.4                                  |         |
| M15 | Azure ML training pipeline (ingest, preprocess, train, evaluate, register)  | Required by ILO 8.9 and ILO 9.4                      |         |
| M16 | Scheduled or trigger-based pipeline execution                               | Required by General Project Requirements and ILO 9.4 |         |
| M17 | Experiment tracking with MLflow (metrics, learning curves, example outputs) | Required by ILO 8.9                                  |         |
| M18 | Cloud deployment on Azure (containerised application)                       | Required by project deliverables and ILO 9.5         |         |
| M19 | CI/CD pipeline via GitHub Actions (lint, test, build, deploy)               | Required by General Project Requirements and ILO 9.5 |         |
| M20 | Model versioning and conditional registration                               | Required by ILO 9.5                                  |         |
| M21 | Automated retraining pipeline (triggered by new data or user feedback)      | Required by General Project Requirements and ILO 9.5 |         |
| M22 | Operational monitoring (latency, error rate, drift detection)               | Required by ILO 9.5                                  |         |
| M23 | PostgreSQL database with metadata schema                                    | Required by project specification                    |         |
| M24 | Architecture diagrams (data pipeline, training pipeline, deployment)        | Required by project deliverables and ILO 4.4         |         |
| M25 | Azure cost analysis and cost management strategy                            | Required by ILO 4.4                                  |         |
| M26 | README with installation, usage, and deployment instructions                | Required by project deliverables                     |         |
| M27 | Package plan (module structure, interfaces, dependencies)                   | Required by project deliverables                     |         |
| M28 | Azure DevOps Boards with product backlog and sprint backlogs                | Required by project deliverables                     |         |
| M29 | Learning log, work log, and peer reviews                                    | Required as a prerequisite for all ILOs              |         |
| M30 | User submission: upload image and receive prediction                        | Core user flow                                       |         |
| M31 | User correction: annotate or flag incorrect predictions                     | Required for retraining loop                         |         |
| M32 | Demo on Demo Day (local, on-premise, cloud)                                 | Required by project deliverables                     |         |
| M33 | Web-based frontend for image submission, prediction display, and user corrections                                | Required by General Project Requirements and ILO 9.5                     |         |

### Should Have

These features significantly improve the quality of the product and are possible within the timeline.

| ID  | Feature                                                                                                      | Justification                                                                   |Completed|
| --- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |---------|
| S01 | Frontend monitoring dashboard with business metrics (confidence trends, correction rate, retraining history) | Required for ILO 10.3; separates operational from stakeholder-facing monitoring |         |
| S02 | Hyperparameter tuning pipeline (e.g., Azure ML sweep)                                                        | Required by ILO 8.9; improves model quality                                     |         |
| S03 | Multi-user support with basic authentication                                                                 | Required by domain brief; needed for secure access to data and models           |         |
| S04 | Model selection by version in the inference pipeline                                                         | Required by ILO 9.5; allows rollback and A/B comparison                         |         |
| S05 | Sphinx-generated documentation site (HTML)                                                                   | Raises documentation quality above inline docstrings alone                      |         |
| S06 | Pre-commit hooks for linting and formatting (Black, Flake8, isort)                                           | Industry best practice; supports ILO 9.3                                        |         |
| S07 | Integration tests for the API endpoints                                                                      | Supports ILO 9.3; catches regressions in the inference pipeline                 |         |
|     |                                                                                                              |                                                                                 |         |

### Could Have

These features would improve the product, but are lower priority and should only be attempted once all **Must Have** and **Should Have** items are completed.

| ID  | Feature                                                                       | Justification                                                             |Completed|
| --- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------- |---------|
| C01 | Explainability visualisations (e.g., GradCAM overlays on segmentation output) | Directly supports the Silver medal challenge; adds scientific value       |         |
| C02 | Batch inference endpoint (process multiple images in one request)             | Useful for research workflows but not required for the MVP                |         |
| C03 | Frontend image annotation tool (draw corrections directly on the image)       | Improves UX for corrections; more complex to implement than a simple flag |         |
| C04 | Automated data quality checks in the ingestion pipeline                       | Good MLOps practice; reduces bad data entering the training loop          |         |
| C05 | Blog post comparing AWS, Azure, and GCP MLOps tools                           | Directly supports the Bronze medal challenge                              |         |

### Won't Have

These features are explicitly out of scope for this project. They are noted here to prevent scope creep.

| ID  | Feature                                                   | Reason out of scope                                                                                      |
| --- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| W01 | Real-time video stream inference                          | Hardware and latency requirements exceed the block scope; static image input is sufficient per the brief |
| W02 | Multi-robot or multi-platform deployment                  | The brief requires platform-agnostic design (M10), but actual multi-robot orchestration is beyond scope  |
| W03 | Mobile application frontend                               | Not required by the brief; web frontend is sufficient                                                    |
| W04 | Fine-grained role-based access control (RBAC)             | Basic authentication (S03) is sufficient for this stage                                                  |
| W05 | Raw image storage in the database                         | Explicit design decision: files are stored on disk/Blob Storage; the database stores metadata only       |
| W06 | Training on GPU clusters beyond standard Azure ML compute | Budget constraints; standard compute is sufficient for the model sizes in scope                          |

## Sprint Milestones and Deadlines

This block runs for 8 working weeks starting on 13 April to 12 June.

Notable Dates within this block:

| Event                  | Notes                            | Dates            |
| ---------------------- | -------------------------------- | ---------------- |
| Block Start            |                                  | 13 April         |
| May Holiday/King's Day | Holiday, no official work        | 27 April - 1 May |
| Ascension Day          | Holiday, no official work        | 14, 15 May       |
| Whit Monday            | Holiday, no official work        | 25 May           |
| End of Block           | All submissions are due by 16:59 | 12 June          |

| Sprint   | Weeks     | Calendar Dates          | Milestone                                                                                                                                                                                                                                    |
| -------- | --------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sprint 1 | Week 1    | 13-17 Apr 2026          | Project plan, package plan, repo structure, Azure DevOps setup, branching strategy, virtual environments configured                                                                                                                          |
| Sprint 2 | Weeks 2-3 | 20 Apr - 8 May 2026     | MVP Python package installable, CLI for inference, FastAPI inference endpoint, Docker containers for backend/frontend/DB, local deployment working, on-premise deployment on Portainer                                                       |
| Sprint 3 | Weeks 4-5 | 11-22 May 2026           | Data in Azure Blob Storage with versioned assets, Azure ML environments registered, training pipeline running in cloud, experiment tracking with MLflow, hyperparameter tuning pipeline, scheduled pipeline trigger, basic frontend deployed |
| Sprint 4 | Weeks 6-7 | 25-29 May and 1-5 Jun 2026 | Cloud deployment on Azure, CI/CD pipeline automated, model versioning and conditional registration, retraining pipeline with user feedback loop, operational monitoring, stakeholder dashboard                                               |
| Sprint 5 | Week 8    | 8-12 Jun 2026           | All outstanding tasks completed, synthetic and real-world testing, Demo Day preparation, final documentation, submission by 12 Jun 16:59                                                                                                     |

Note: Week of 27-30 Apr and 1 of May (holiday) is not counted. Sprint 4 therefore spans week 6 (25-29 May), then resumes weeks 7 (1-5 Jun) after the holiday break.

## Feature-to-Sprint Mapping

See [MoScOw Feature Propitiation](#moscow-feature-prioritization) for ID correspondence.

### Sprint 1 — Planning and Setup

M24, M25, M27, M28, M29, M26 (initial README), plus repo and environment setup (supports M04, M08).

Goals: Architecture diagrams drafted, cost analysis started, package plan written, Azure DevOps boards populated with full backlog, GitHub repo with protected branches and branching strategy, virtual environments and dependency management configured.

### Sprint 2 — MVP Inference Application

M04, M05, M06, M07, M08, M09, M10, M11, M12, M23, M30, S06, S07.

Goals: Installable Python package with CLI, logging, error handling, docstrings, and unit tests. FastAPI endpoint for inference (segmentation masks, root-tip coordinates, confidence scores). Docker Compose stack (backend, frontend stub, PostgreSQL). Local and on-premise deployment verified. Database schema for submission metadata in place.

This is a **Minimal Viable Product** - the focus should be to produce a working stack. It is OK to have rough edges and barely functional features, but the product should have basic functionality.

### Sprint 3 — Data Pipelines and Cloud Training

M13, M14, M15, M16, M17, S01 (partial), S02, S05 (partial).

Goals: Data uploaded to Azure Blob Storage with versioned data assets. Azure ML environments registered. Full training pipeline (ingest, preprocess, train, evaluate, conditionally register) running in the cloud. MLflow experiment tracking with metrics and learning curves. Hyperparameter tuning sweep configured. Pipeline scheduled or trigger-based. Basic frontend with prediction display deployed.

### Sprint 4 — Deployment, Monitoring, and Retraining

M18, M19, M20, M21, M22, M31, S01 (complete), S03, S04.

Goals: Application deployed to Azure. CI/CD pipeline automated via GitHub Actions (lint, test, build, push image, deploy). Registered models deployed as Azure ML endpoints with version selection. User correction workflow implemented (M31). Automated retraining pipeline triggered by new data or corrections. Operational monitoring live. Stakeholder dashboard with business metrics in the frontend.

### Sprint 5 — Testing, Evaluation, and Demo

M32, C01 (if capacity), C02 (if capacity), M26 (finalised), M29 (finalised).

Goals: Synthetic load tests and real-world user tests completed. Demo Day setup (4 screens: live app, documentation, poster, evidence). All deliverables submitted to GitHub by 12 Jun 16:59.

## Dependency Mapping

The following dependencies must be respected when scheduling tasks within sprints.

| Feature                       | Depends On                                                  |
| ----------------------------- | ----------------------------------------------------------- |
| M09 (FastAPI endpoint)        | M04 (Python package), M01, M02, M03 (model outputs defined) |
| M10 (Docker containers)       | M09, M23 (DB schema)                                        |
| M11 (local deployment)        | M10                                                         |
| M12 (on-premise deployment)   | M11                                                         |
| M14 (Azure data assets)       | M04 (data scripts in package)                               |
| M15 (training pipeline)       | M13 (Azure ML workspace), M14                               |
| M17 (MLflow tracking)         | M15                                                         |
| M18 (cloud deployment)        | M10, M15, M20                                               |
| M19 (CI/CD)                   | M10, M07 (tests must exist before automation)               |
| M20 (model versioning)        | M15, M17                                                    |
| M21 (retraining pipeline)     | M15, M31 (user corrections feed data back)                  |
| M22 (operational monitoring)  | M18                                                         |
| M31 (user corrections)        | M30 (users must first receive a prediction), M23            |
| S01 (stakeholder dashboard)   | M22, M31                                                    |
| S02 (hyperparameter tuning)   | M15                                                         |
| S03 (authentication)          | M09, M23                                                    |
| S04 (model version selection) | M20                                                         |
| C01 (explainability)          | M09, M18                                                    |

## Team Responsibilities

Roles are assigned per sprint and rotated where feasible. Each team member must demonstrate individual contribution to the codebase for ILO 9.3.

| Role                     | Responsibility                                                                        |
| ------------------------ | ------------------------------------------------------------------------------------- |
| Scrum Master (rotating)  | Sprint planning, standups, retrospectives, Azure DevOps board maintenance             |
| ML Engineer              | Model integration, training pipeline, MLflow tracking, hyperparameter tuning          | - Lars Peggeamn (241863) Can do
| MLOps / Infrastructure   | Docker, CI/CD, Azure deployment, monitoring setup                                     | - Lars Peggeamn (241863) Cam do
| Data Engineer            | Data ingestion pipeline, Azure Blob Storage, versioned data assets, PostgreSQL schema | - Lars Peggeamn (241863) Weakness, great with SQL
| Frontend / Visualisation | Frontend application, monitoring dashboard, user submission and correction UI         | - Lars Peggeman (241863) Personal favourite

All team members contribute to the Python package, documentation, and testing. Individual contributions must be traceable via Git commit history and the learning log.

*This document should be updated at the start of each sprint to reflect progress, re-prioritised items, and any changes to scope agreed with the product owner.*
