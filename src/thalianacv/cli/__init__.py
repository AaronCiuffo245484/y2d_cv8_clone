"""CLI for local inference and model management.

Wraps the core inference pipeline so that users can run predictions
from the command line without writing Python code.
"""

import typer

app = typer.Typer()

from thalianacv.cli import main  # noqa: E402, F401
