## What

Describe what this PR does. Focus on the change itself, not the reason for it.

Example: Adds an image normalisation function to the preprocessing module.

## Why

Explain why this change is needed. Reference the Azure Boards work item ID.

Example: Normalisation is required before images can be passed to the model. Implements work item #271.

## Unit Tests

- [ ] I Have added unit tests for functions
- [ ] Unit tests are passing

## Docstrings

- [ ] I Have added docstrings to all functions
- [ ] Sphinx documentation is building correctly

> hint: change - [ ] to - [x] to show as a completed item

## How to verify

List the steps a reviewer can follow to confirm the change works correctly.

Example:
1. Pull the branch and run `poetry run pytest tests/ -v`
2. All tests should pass
3. Run `poetry run black --check .` and confirm no formatting issues

> HINT: Your favorite LLM can help you write this well
