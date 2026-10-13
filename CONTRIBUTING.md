# Contributing to ai-panorama-360-generator

Thanks for wanting to help build the panorama rig. This repo is a Python
desktop tool that turns prompts / reference images into equirectangular
360 panoramas and cubemaps using tiled diffusion, seam-aware stitching,
and depth-guided outpainting.

## Development setup

```powershell
git clone https://github.com/panorama-360/ai-panorama-360-generator
cd ai-panorama-360-generator
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,cuda]"
pre-commit install
```

CPU-only contributors: drop the `cuda` extra. Tiled generation on CPU is
slow but fully supported for tests and small resolutions.

## Layout

- `panorama360/handlers/` — ingest handlers (prompt, image, depth, cubemap)
- `panorama360/processors/` — diffusion, tiling, seam, depth processors
- `panorama360/drivers/` — output drivers (equirect PNG, cubemap, EXR, VR preview)
- `panorama360/services/` — orchestration, model cache, job queue
- `panorama360/models/` — pydantic schemas for jobs, tiles, projections
- `panorama360/utils/` — geometry, image ops, logging, paths
- `panorama360/config/` — default TOML configs and presets

## Adding a new processor

1. Subclass `processors.base.BaseProcessor`.
2. Register it in `processors/__init__.py` under `PROCESSOR_REGISTRY`.
3. Add a pydantic config in `models/pipeline.py`.
4. Add a test under `tests/`.

## Adding a new output driver

1. Subclass `drivers.base.OutputDriver`.
2. Implement `write(panorama: PanoramaTensor, path: Path) -> Path`.
3. Register in `drivers/__init__.py` under `DRIVER_REGISTRY`.

## Style

- `ruff format` + `ruff check --fix` before commits.
- `mypy --strict` must pass on `panorama360/`.
- No new runtime deps without an issue thread first.
- Keep tile math in `utils/geometry.py` — do not duplicate it in processors.

## Pull requests

- One concern per PR. Tiling fixes don't ride along with UI tweaks.
- Include a repro command for any bug fix.
- Screenshots of generated panoramas welcome in the PR body.