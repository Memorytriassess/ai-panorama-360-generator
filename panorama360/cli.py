"""Command-line entry point for the panorama 360 generator.

Runtime: Python 3.11+, Windows-first, CUDA optional.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console

from panorama360.models.job import JobSpec, ProjectionKind
from panorama360.services.orchestrator import Orchestrator
from panorama360.utils.logging import configure_logging

app = typer.Typer(
    name="panorama360",
    help="AI panorama / 360 generator — diffusion-backed equirect and cubemap synthesis.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command("generate")
def generate(
    prompt: str = typer.Argument(..., help="Scene prompt for the panorama."),
    out: Path = typer.Option(Path("artifacts/renders/pano.png"), "--out", "-o"),
    width: int = typer.Option(4096, "--width", "-w", help="Equirect width in px."),
    height: int = typer.Option(2048, "--height", "-h", help="Equirect height in px."),
    projection: ProjectionKind = typer.Option(ProjectionKind.EQUIRECT, "--projection", "-p"),
    steps: int = typer.Option(28, "--steps"),
    seed: Optional[int] = typer.Option(None, "--seed"),
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Generate a single panorama from a text prompt."""
    configure_logging(verbose=verbose)
    spec = JobSpec(
        prompt=prompt,
        output_path=out,
        width=width,
        height=height,
        projection=projection,
        steps=steps,
        seed=seed,
        config_path=config,
    )
    orchestrator = Orchestrator.from_defaults()
    result = asyncio.run(orchestrator.run_job(spec))
    console.print(f"[green]wrote[/green] {result.output_path} ({result.tile_count} tiles, {result.elapsed_s:.1f}s)")


@app.command("batch")
def batch(
    manifest: Path = typer.Argument(..., exists=True, readable=True),
    out_dir: Path = typer.Option(Path("artifacts/renders"), "--out-dir"),
    workers: int = typer.Option(2, "--workers", min=1, max=8),
) -> None:
    """Run a batch of jobs from a JSON manifest."""
    configure_logging(verbose=False)
    orchestrator = Orchestrator.from_defaults()
    asyncio.run(orchestrator.run_manifest(manifest, out_dir=out_dir, workers=workers))
    logger.info("batch complete: {}", manifest)


@app.command("doctor")
def doctor() -> None:
    """Check environment: torch, CUDA, model cache, plugin dir."""
    from panorama360.services.diagnostics import run_diagnostics

    report = run_diagnostics()
    for line in report.lines:
        console.print(line)
    raise typer.Exit(code=0 if report.ok else 1)


if __name__ == "__main__":
    app()