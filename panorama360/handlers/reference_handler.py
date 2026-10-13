"""Load a reference image, strip EXIF, resize to tile-friendly dimensions."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from loguru import logger
from PIL import Image, ImageOps

from panorama360.handlers.base import BaseHandler, HandlerContext
from panorama360.utils.image_ops import to_float01


class ReferenceImageHandler(BaseHandler):
    name = "reference"

    async def handle(self, ctx: HandlerContext) -> HandlerContext:
        ref_path = ctx.spec.reference_image
        if ref_path is None:
            return ctx
        resolved = self._resolve(ref_path)
        if not resolved.exists():
            raise FileNotFoundError(f"reference image not found: {resolved}")

        with Image.open(resolved) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            # Cap the long edge to the tile size to keep VRAM predictable.
            max_edge = max(ctx.config.tile.tile_w, ctx.config.tile.tile_h)
            im.thumbnail((max_edge, max_edge), Image.LANCZOS)
            arr = to_float01(np.asarray(im))

        ctx.reference = arr
        logger.debug("reference loaded {} -> {}", resolved.name, arr.shape)
        return ctx