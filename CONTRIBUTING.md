# Contributing to CV8 — Plant Segmentation Pipeline <!-- omit in toc -->

This document describes the conventions and workflows that all contributors must follow.

- [Workflow](#workflow)
- [Daily workflow](#daily-workflow)
- [Docker](#docker)
- [Branch naming](#branch-naming)
- [Environment setup](#environment-setup)
- [Jupyter notebooks](#jupyter-notebooks)
- [Pre-commit hooks](#pre-commit-hooks)
- [Documentation](#documentation)
- [Code formatting](#code-formatting)
- [Function structure](#function-structure)

---

## Workflow

This project follows [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow).

GitHub Flow is a lightweight, branch-based workflow. The rules are:

1. `main` is always deployable. Never commit directly to `main`.
2. Create a branch from `main` for every piece of work.
3. Add commits to your branch. Push regularly.
4. Open a pull request when your work is ready for review.
5. At least one team member must review and approve the pull request before it is merged.
6. After approval, merge into `main` and delete the branch.

Do not merge your own pull request without a review from another team member.

### Pull request scope

Each pull request must do exactly one thing. Do not mix unrelated changes in a single PR.

**Examples of acceptable PRs:**

- Add the image preprocessing module
- Fix the off-by-one error in the crop function
- Refactor the pipeline to remove duplicated logic
- Update the README with deployment instructions

**Examples of PRs that should be split:**

- Add preprocessing module and fix unrelated import error — split into two PRs
- Reformat files and add new feature — split into two PRs

### Pull request description

Every PR must include a description that answers these three questions:

1. What does this PR do?
2. Why is this change needed?
3. How can the reviewer test or verify it?

Use this template when opening a PR:

```
## What
A short description of the change.

## Why
The reason this change is needed.

## How to verify
Steps the reviewer can follow to check that the change works correctly.
```

A PR that lacks a description or mixes unrelated changes should be returned to the author before review begins.

---

## Daily workflow

This section gives a concrete recipe for managing your work day. Following it consistently will prevent most merge conflicts and keep the team unblocked.

### Starting your day

Before writing any code, bring your feature branch up to date with `main`.

```bash
git checkout main
git pull origin main
git checkout 'feature/<id>-<description>'
git merge main
```

If there are no conflicts, continue working. If there are conflicts, resolve them before doing anything else — do not commit new work on top of unresolved conflicts.

### suggested tools

```choco install make```
- install guidelines and documentation


### Making commits during the day

Commit small and often. Each commit should represent one coherent change. This makes it easier to find problems and easier for reviewers to follow your work.

**Always stage your files before committing.** Pre-commit hooks run on staged files. If a file has both staged and unstaged changes at the same time, the hooks will fail.

**To commit all changed files:**

```bash
git add .
git commit -m "<type>: <short description>"
```

**To commit a single file:**

If you only want to commit one file and have other files with unsaved changes, stash the unstaged changes first:

```bash
git add <file>
git stash --keep-index
git commit -m "<type>: <short description>"
git stash pop
```

`git stash --keep-index` temporarily sets aside everything that is not staged. After the commit succeeds, `git stash pop` restores those changes.

**To check what is staged before committing:**

```bash
git status
```

Files under `Changes to be committed` will be included in the commit. Files under `Changes not staged for commit` will not.

Commit message types follow the same convention as branch names: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

**Examples:**

```
feat: add image normalisation to preprocessing pipeline
fix: correct off-by-one error in crop function
test: add unit tests for normalisation function
docs: update README with usage examples
```

Push to your remote branch regularly so your work is not only on your machine:

```bash
git push origin 'feature/<id>-<description>'
```
## Docker

This project uses Docker and Docker Compose to run the application stack locally
and on-premise via Portainer.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Running the stack locally

From the repo root:

```bash
make docker-up
```

This builds all images and starts all containers. To stop the stack:

```bash
make docker-down
```

To build without starting:

```bash
make docker-build
```

### Services

The `docker-compose.yml` file defines the following services:

| Service | Port | Description |
|---------|------|-------------|
| `api` | 8000 | FastAPI inference endpoint |

Additional services (frontend, database) will be added as they are built.
Ports 2031-2035 are available for on-premise deployment.

### Adding a new service

Add your service block to `docker-compose.yml` alongside the existing ones:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"

  your-service:       # add your block here
    build: ./your-service-directory
    ports:
      - "XXXX:XXXX"
```

Each service lives in its own block — do not modify existing service blocks
when adding a new one.

### On-premise deployment (Portainer)

The application can be deployed to the BUAS on-premise server via Portainer.
Portainer is only accessible on campus or via VPN.

Containers must be registered on GHCR (GitHub Container Registry) and pulled
via Docker Compose files. Ports 2031-2035 are available for our containers.

Contact a team member for the Portainer IP and credentials.

### Verifying the stack

Once the stack is running, verify each service is responding on its expected port.
Refer to the services table above for the port mappings.

### Makefile shortcuts

| Command | Description |
|---------|-------------|
| `make docker-build` | Build all Docker images |
| `make docker-up` | Build and start the full stack |
| `make docker-down` | Stop and remove all containers |


### Ending your day

Before stopping work, push everything to the remote branch.

```bash
git add .
git commit -m "<type>: <description of where things are>"
git push origin 'feature/<id>-<description>'
```

It is fine to commit work in progress at the end of the day. Use a clear message so your future self knows the state of things, for example `feat: wip - normalisation working, augmentation not started`.

### When your PR is ready

1. Bring your branch up to date with `main` one final time before opening the PR:

```bash
git checkout main
git pull origin main
git checkout 'feature/<id>-<description>'
git merge main
git push origin 'feature/<id>-<description>'
```

2. Open the PR on GitHub using the PR description template.
3. Wait for both CI checks to pass before requesting a review.
4. Do not merge your own PR.

### A note on merging vs rebasing

This project uses squash merge for all PRs into `main`. This means each PR becomes a single commit on `main`. As a result, you must use `git merge` (not `git rebase`) when bringing `main` into your feature branch. Rebasing a squash-merge workflow causes conflicts that are difficult to resolve.

Never run `git rebase main` on a feature branch in this project.

---

## Branch naming

Branch names must follow this pattern:

```
<type>/<azure-boards-id>-<short-description>
```

`<type>` must be one of:

| Type | Use for |
|------|---------|
| `feature` | New functionality |
| `fix` | Bug fixes |
| `docs` | Documentation only changes |
| `refactor` | Code restructuring with no behaviour change |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks such as dependencies or config |

`<azure-boards-id>` is the work item ID from Azure Boards. Always create or find a work item before creating a branch.

`<short-description>` must be lowercase and hyphen-separated.

**Examples:**

```
feature/271-ci-setup
fix/304-image-preprocessing-crop
docs/289-update-readme
refactor/312-pipeline-modularisation
test/298-segmentation-unit-tests
chore/275-update-torch-dependency
```

Branch names that do not match this pattern will be rejected by the repository.

Note: always quote branch names in the terminal to prevent the shell from interpreting special characters:

```bash
git checkout -b 'feature/271-ci-setup'
git push origin 'feature/271-ci-setup'
```

---

## Environment setup

This project requires Python 3.10 and uses [uv](https://docs.astral.sh/uv/) for dependency and virtual environment management.

### Installing uv on Windows

```PowerShell
winget install astral-sh.uv
```

After installation, open a new terminal and verify:

```PowerShell
uv --version
```

### Installing uv on Mac/Linux

```bash
brew install uv
```

Or using the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installation, restart your terminal and verify:

```bash
uv --version
```

### Setting up the project

**1. Clone the repository**

```bash
git clone git@github.com:BredaUniversityADSAI/2025-26d-fai2-adsai-group-computervision8.git
cd thalianacv
```

**2. Configure Git line endings**

This is a one-time setting per machine. It ensures consistent line endings across Mac, Linux, and Windows and prevents pre-commit from failing due to OS-level line ending conversion.

```bash
git config core.autocrlf false
```

Then re-normalise the repository files:

```bash
git rm --cached -r .
git reset --hard
```

**3. Install dependencies**

```bash
uv sync
```

This creates a `.venv` directory in the project root and installs all dependencies from `uv.lock`. Do not delete or modify `uv.lock` manually.

**4. Install pre-commit hooks**

```bash
uv run pre-commit install --overwrite
```

This wires pre-commit into your local git hooks so checks run automatically on every commit.

**5. Verify your setup**

```bash
uv run pytest tests/ -v
```

All tests should pass before you begin working.

---

## Jupyter notebooks

Notebooks live in the `notebooks/` directory. This directory is tracked but its contents are excluded by `.gitignore` by default. Do not commit notebooks unless there is a specific reason to share output with the team.

### Setting up the kernel in VS Code

Install the `ipykernel` package into the uv environment:

```bash
uv add --dev ipykernel
```

Register the kernel so VS Code can find it:

```bash
uv run python -m ipykernel install --user --name thalianacv --display-name "thalianacv"
```

In VS Code, open a notebook and select the kernel by clicking the kernel picker in the top right. Choose `thalianacv` from the list. This ensures the notebook uses the same environment as the rest of the project.

### Activating the virtual environment for interactive use

If you need to run `python` or `jupyter` directly in a terminal without prefixing every command with `uv run`, activate the virtual environment manually:

```bash
# macOS and Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Deactivate when done:

```bash
deactivate
```

### Committing a notebook

Notebooks are excluded by default. To include a specific notebook, add an explicit exception to `.gitignore`:

```
!notebooks/my_notebook.ipynb
```

Before committing a notebook, clear all output to avoid large diffs and binary data in the repo. In VS Code, open the notebook and select `Clear All Outputs` from the command palette (`Cmd+Shift+P` on Mac, `Ctrl+Shift+P` on Windows/Linux).

Then stage and commit as normal:

```bash
git add notebooks/my_notebook.ipynb
git commit -m "docs: add my_notebook results"
```

---

## Pre-commit hooks

Pre-commit hooks run automatically every time you run `git commit`. They check and fix your code before it enters the repository. Understanding what each tool does and how to respond when a hook fails is essential for a smooth workflow.

### What each tool does

**Black** is a code formatter. It automatically fixes spacing, line length, and other formatting issues. It never blocks a commit — it modifies the file and you stage the changes again.

**isort** sorts and groups import statements automatically. Like Black, it fixes the file rather than blocking.

**Flake8** is a linter. It catches unused imports, undefined variables, and other code quality issues that Black cannot fix. It does block commits and requires you to fix the problems manually.

### What to do when a hook fails

**If Black or isort modified files:**

The tools have already fixed the problem. Stage the changes and commit again:

```bash
git add .
git commit -m "your original message"
```

**If Flake8 fails:**

Flake8 will print the file, line number, and error code for each problem. Fix each one manually, then stage and commit again:

```bash
# Example Flake8 output:
# thalianacv/module.py:3:1: F401 'os' imported but unused
# thalianacv/module.py:12:5: F841 local variable 'x' is assigned to but never used

# Fix the problems in your editor, then:
git add .
git commit -m "your original message"
```

Common Flake8 error codes:

| Code | Meaning | Fix |
|------|---------|-----|
| F401 | Imported but unused | Remove the import |
| F841 | Local variable assigned but never used | Remove the variable or use it |
| F821 | Undefined name | Define the variable or import it |
| E501 | Line too long | Black handles this automatically |

### Practising with pre-commit hooks

To understand how the hooks work, follow these steps on the practice branch `chore/860-commit-practice`.

**1. Create a file with deliberate violations:**

```python
import os
import sys
import json
from thalianacv import hello

x=1
y = 2+3

def bad_function(a,b,c):
    unused = "this variable is never used"
    return a+b
```

**2. Stage it and run pre-commit to see what happens:**

```bash
git add thalianacv/practice.py
uv run pre-commit run --all-files
```

**3. See what Black and isort auto-fixed:**

```bash
git diff thalianacv/practice.py
```

**4. Restore the original bad file:**

```bash
git checkout -- thalianacv/practice.py
```

**5. Bypass pre-commit to push the bad code as-is:**

```bash
git add thalianacv/practice.py
git commit --no-verify -m "chore: add practice file with violations"
git push origin 'chore/860-commit-practice'
```

**6. Fix the violations and commit properly:**

```bash
git add thalianacv/practice.py
uv run pre-commit run --all-files
git add thalianacv/practice.py
git commit -m "chore: fix violations in practice file"
git push origin 'chore/860-commit-practice'
```

Note: `--no-verify` bypasses pre-commit entirely. Never use it on a real feature branch — it exists only for practice and debugging purposes.

---

## Documentation

This project uses [Sphinx](https://www.sphinx-doc.org/) to generate HTML documentation from docstrings. The documentation source lives in `docs/`. Built output is excluded from the repository via `.gitignore`.

### How documentation is generated

Sphinx reads `docs/api/index.rst`, which contains `automodule` directives for each submodule. These directives tell Sphinx to import the module and extract all docstrings at build time. No stub files are generated or committed.

### When you add a new submodule

Add an entry to `docs/api/index.rst` for your new submodule. For example, if you add `thalianacv/pipeline.py`:

```rst
thalianacv.pipeline
-------------------

.. automodule:: thalianacv.pipeline
   :members:
   :undoc-members:
   :show-inheritance:
```

Commit `docs/api/index.rst` alongside your new module.

### Building the docs locally

```bash
uv run sphinx-build -b html docs/ docs/_build/html
```

Open `docs/_build/html/index.html` in a browser to review the output.

### When the sphinx-build pre-commit hook fails

The hook runs `sphinx-build` before every commit. If it fails, the most likely cause is that you added a new submodule but did not update `docs/api/index.rst`. Add the missing `automodule` entry as described above, then stage and commit again:

```bash
git add docs/api/index.rst
git commit -m "your original message"
```

---

## Code formatting

All code must be formatted with [Black](https://black.readthedocs.io/en/stable/) before committing. Pre-commit will run Black automatically on every commit and block the commit if formatting issues are found.

**Run Black manually:**

```bash
uv run black .
```

**Check without modifying files:**

```bash
uv run black --check .
```

The following rules apply to all code in this repository:

- Maximum line length is 88 characters (Black's default).
- File encoding is UTF-8.
- File and variable names use `snake_case`.
- Do not use wildcard imports (`from module import *`).
- Each module has one concern. For example, `train.py` handles training, `predict.py` handles inference. Do not put unrelated logic in the same file.

---

## Function structure

All functions must follow these conventions:

- Type hints on all parameters and return values.
- Google style docstrings on all public functions.
- One function, one responsibility. If a function is doing two unrelated things, split it.

**Example:**

```python
def preprocess_image(image_path: str, target_size: tuple[int, int]) -> np.ndarray:
    """Load and resize an image for model inference.

    Args:
        image_path: Path to the input image file.
        target_size: Target dimensions as (width, height).

    Returns:
        A normalised NumPy array of shape (H, W, C).

    Raises:
        FileNotFoundError: If the image file does not exist at image_path.
        ValueError: If target_size contains non-positive integers.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    if any(dim <= 0 for dim in target_size):
        raise ValueError(f"target_size must contain positive integers, got {target_size}")

    image = cv2.imread(image_path)
    image = cv2.resize(image, target_size)
    image = image.astype(np.float32) / 255.0

    return image
```

Note the following in the example above:

- The docstring describes what the function does, not how it does it.
- `Args`, `Returns`, and `Raises` sections are all present.
- Type hints are on the signature, not repeated in the docstring.
- The function does one thing: load and preprocess an image.

---

document-version: 6 260424.1400
