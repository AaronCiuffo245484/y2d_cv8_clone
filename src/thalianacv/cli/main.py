"""CLI predict command for single-image inference."""

import typer

from thalianacv.cli import app
from thalianacv.core.predict import predict as run_predict


@app.command(
    name="predict", help="Run the full inference pipeline on a single plant image."
)
def predict_command(
    image_path: str,
    shoot_model_path: str = typer.Option(..., help="Path to shoot segmentation model"),
    root_model_path: str = typer.Option(..., help="Path to root segmentation model"),
    global_stats_path: str | None = typer.Option(
        None, help="Path to global stats file"
    ),
) -> None:
    """Run the full inference pipeline on a single plant image.

    Args:
        image_path: Path to the input plant image.
        shoot_model_path: Path to the shoot segmentation model.
        root_model_path: Path to the root segmentation model.
        global_stats_path: Path to the global stats file.
            Defaults to None.
    """
    result = run_predict(
        image_path,
        shoot_model_path,
        root_model_path,
        global_stats_path,
    )

    typer.echo(f"Confidence score: {result.confidence_score}")
    typer.echo(f"Shoot mask shape: {result.shoot_mask.shape}")
    typer.echo(f"Root mask shape: {result.root_mask.shape}")
    typer.echo(f"Coordinates:\n {result.coordinates}")
