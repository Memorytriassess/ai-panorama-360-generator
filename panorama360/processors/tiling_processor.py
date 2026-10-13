"""Compute the tile grid for the target canvas.

This processor is pure geometry — no model calls. It populates
`ctx.scratch['tile_grid']` for the diffusion processor to consume.
"""

from __future__ import annotations

import math

from loguru import logger

from panorama360.handlers.base import HandlerContext
from panorama360.models.panorama import PanoramaTensor, TileGrid
from panorama360.processors.base import BaseProcessor


class TilingProcessor(BaseProcessor):
    name = "tiling"
    provides = ("tile_grid",)

    async def process(self, ctx: HandlerContext) -> PanoramaTensor:
        cfg = ctx.config.tile
        w, h = ctx.spec.width, ctx.spec.height
        step_x = cfg.tile_w - cfg.overlap
        step_y = cfg.tile_h - cfg.overlap
        cols = max(1, math.ceil((w - cfg.overlap) / step_x))
        rows = max(1, math.ceil((h - cfg.overlap) / step_y))
        grid = TileGrid(
            cols=cols,
            rows=rows,
            tile_w=cfg.tile_w,
            tile_h=cfg.tile_h,
            overlap=cfg.overlap,
        )
        ctx.scratch["tile_grid"] = grid
        logger.info("tile grid {}x{} = {} tiles", cols, rows, grid.total)
        # Placeholder panorama; diffusion processor overwrites the image.
        import numpy as np

        return PanoramaTensor(
            image=np.zeros((h, w, 3), dtype=np.float32),
            projection=ctx.spec.projection.value,  # type: ignore[arg-type]
            grid=grid,
        )