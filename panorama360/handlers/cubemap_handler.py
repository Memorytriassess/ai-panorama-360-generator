"""Seed latents from a 6-face cubemap input.

Used when the user already has a cubemap and wants it re-projected into
an equirect panorama with AI-consistent fill between faces.
"""

from __future__ import annotations

import numpy as np
from loguru import logger

from panorama360.handlers.base import BaseHandler, HandlerContext
from panorama360.utils.geometry import cubemap_faces_to_equirect


class CubemapSeedHandler(BaseHandler):
    name = "cubemap_seed"

    FACE_ORDER = ("px", "nx", "py", "ny", "pz", "nz")

    async def handle(self, ctx: HandlerContext) -> HandlerContext:
        faces_dir = ctx.scratch.get("cubemap_dir")
        if not faces_dir:
            return ctx
        from pathlib import Path

        from PIL import Image

        from panorama360.utils.image_ops import to_float01

        faces: list[np.ndarray] = []
        for face in self.FACE_ORDER:
            p = Path(faces_dir) / f"{face}.png"
            if not p.exists():
                raise FileNotFoundError(f"missing cubemap face: {p}")
            with Image.open(p) as im:
                faces.append(to_float01(np.asarray(im.convert("RGB"))))

        equirect = cubemap_faces_to_equirect(
            faces, ctx.spec.width, ctx.spec.height
        )
        ctx.scratch["seed_equirect"] = equirect
        logger.debug("cubemap seed assembled: {}", equirect.shape)
        return ctx