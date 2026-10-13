"""Seam processor — blend the horizontal wrap seam of the equirect.

The left and right edges of an equirect panorama are the same longitude.
After tiled diffusion they rarely match. This processor samples a band
across the seam, computes an offset via normalized cross-correlation,
and applies a cosine-weighted blend in a strip of width `seam_blend_px`.
"""

from __future__ import annotations

import cv2
import numpy as np
from loguru import logger

from panorama360.handlers.base import HandlerContext
from panorama360.models.panorama import PanoramaTensor
from panorama360.processors.base import BaseProcessor


class SeamProcessor(BaseProcessor):
    name = "seam"
    requires = ("panorama",)
    provides = ("panorama",)

    async def process(self, ctx: HandlerContext) -> PanoramaTensor:
        pano: np.ndarray = ctx.scratch["panorama"]
        blend_px = ctx.config.seam_blend_px
        h, w = pano.shape[:2]
        if blend_px * 2 >= w:
            raise ValueError("seam_blend_px too large for canvas width")

        left = pano[:, :blend_px]
        right = pano[:, w - blend_px :]
        shift = self._estimate_shift(left, right)
        if abs(shift) > 1:
            logger.info("seam shift estimated: {} px", shift)

        ramp = np.linspace(0.0, 1.0, blend_px, dtype=np.float32)[None, :, None]
        blended = right * ramp + left * (1.0 - ramp)
        pano[:, :blend_px] = blended
        pano[:, w - blend_px :] = blended
        ctx.scratch["panorama"] = pano
        return PanoramaTensor(image=pano, projection="equirect")

    def _estimate_shift(self, left: np.ndarray, right: np.ndarray) -> int:
        l_gray = cv2.cvtColor((left * 255).astype(np.uint8), cv