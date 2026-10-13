"""Load or synthesize a depth map for depth-guided outpainting.

If the job provides a depth map, it is loaded and resized. Otherwise the
DepthProcessor downstream synthesizes one from the reference image.
"""

from __future__ import annotations

import numpy as np
from loguru import logger
from PIL import Image

from panorama360.handlers.base import BaseHandler, HandlerContext
from panorama360.utils.image_ops import to_float01, resize_to


class DepthHandler(BaseHandler):
    name = "depth"

    async def handle(self, ctx: HandlerContext) -> HandlerContext:
        depth_path = ctx.spec.depth_map
        if depth_path is None:
            return ctx
        resolved = self._resolve(depth_path)
        if not resolved.exists():
            raise FileNotFoundError(f"depth map not found: {resolved}")

        with Image.open(resolved) as im:
            gray = im.convert("L")
            arr = to_float01(np.asarray(gray))

        target = (ctx.config.tile.tile_h, ctx.config.tile.tile_w)
        ctx.depth = resize_to(arr, target)
        logger.debug("depth map loaded {} -> {}", resolved.name, ctx.depth.shape)
        return ctx