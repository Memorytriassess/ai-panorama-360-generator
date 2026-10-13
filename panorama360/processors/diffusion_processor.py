"""Tiled diffusion processor — the core of the panorama rig.

Loads the base SDXL panorama model, iterates tiles in a serpentine
order (left-to-right, then right-to-left on the next row) so adjacent
tiles share context, and blends each tile into the canvas with a
feathered mask. The pole rows use a boosted vertical overlap to hide
the equirect singularity.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import torch
from loguru import logger

from panorama360.handlers.base import HandlerContext
from panorama360.models.panorama import PanoramaTensor, TileGrid
from panorama360.processors.base import BaseProcessor
from panorama360.services.model_cache import ModelCache
from panorama360.utils.image_ops import feather_mask


class DiffusionProcessor(BaseProcessor):
    name = "diffusion"
    requires = ("tile_grid",)
    provides = ("panorama",)

    def __init__(self, cache: ModelCache | None = None) -> None:
        self._cache = cache or ModelCache()

    async def process(self, ctx: HandlerContext) -> PanoramaTensor:
        grid: TileGrid = ctx.scratch["tile_grid"]
        pipe = self._cache.get_pipeline(ctx.config.base_model, ctx.config)
        generator = self._make_generator(ctx)
        canvas = np.zeros((ctx.spec.height, ctx.spec.width, 3), dtype=np.float32)
        weight = np.zeros((ctx.spec.height, ctx.spec.width, 1), dtype=np.float32)

        for idx, (col, row) in enumerate(self._serpentine(grid)):
            x, y = grid.tile_origin(col, row)
            tile = self._render_tile(pipe, ctx, generator, col, row)
            self._blend(canvas, weight, tile, x, y, grid, row)
            if idx % 8 == 0:
                logger.debug("tile {}/{} done", idx + 1, grid.total)

        canvas = np.clip(canvas / np.maximum(weight, 1e-6), 0.0, 1.0)
        ctx.scratch["panorama"] = canvas
        return PanoramaTensor(
            image=canvas,
            projection=ctx.spec.projection.value,  # type: ignore[arg-type]
            grid=grid,
            metadata={"model": ctx.config.base_model, "steps": str(ctx.spec.steps)},
        )

    def _serpentine(self, grid: TileGrid):
        for row in range(grid.rows):
            cols = range(grid.cols) if row % 2 == 0 else range(grid.cols - 1, -1, -1)
            for col in cols:
                yield col, row

    def _make_generator(self, ctx: HandlerContext) -> Any:
        seed = ctx.spec.seed if ctx.spec.seed is not None else int(np.random.default_rng().integers(0, 2**31))
        device = "cuda" if ctx.config.device == "cuda" and torch.cuda.is_available() else "cpu"
        return torch.Generator(device=device).manual_seed(seed)

    def _render_tile(
        self,
        pipe: Any,
        ctx: HandlerContext,
        generator: Any,
        col: int,
        row: int,
    ) -> np.ndarray:
        cfg = ctx.config.tile
        out = pipe(
            prompt=ctx.prompt,
            negative_prompt=ctx.negative_prompt,
            width=cfg.tile_w,
            height=cfg.tile_h,
            num_inference_steps=ctx.spec.steps,
            guidance_scale=ctx.spec.guidance,
            generator=generator,
        )
        arr = out.images[0]
        return np.asarray(arr, dtype=np.float32) / 255.0

    def _blend(
        self,
        canvas: np.ndarray,
        weight: np.ndarray,
        tile: np.ndarray,
        x: int,
        y: int,
        grid: TileGrid,
        row: int,
    ) -> None:
        th, tw = tile.shape[:2]
        y0, y1 = y, min(y + th, canvas.shape[0])
        x0, x1 = x, min(x + tw, canvas.shape[1])
        th_c, tw_c = y1 - y0, x1 - x0
        mask = feather_mask(th_c, tw_c, grid.overlap)
        canvas[y0:y1, x0:x1] += tile[:th_c, :tw_c] * mask
        weight[y0:y1, x0:x1] += mask