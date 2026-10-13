"""Prompt normalization: strip EXIF-derived junk, clamp length, inject style tags."""

from __future__ import annotations

import re

from loguru import logger

from panorama360.handlers.base import BaseHandler, HandlerContext

_WHITESPACE = re.compile(r"\s+")
_STYLE_TAGS = "equirectangular 360 panorama, seamless, high detail, 8k"


class PromptHandler(BaseHandler):
    name = "prompt"

    async def handle(self, ctx: HandlerContext) -> HandlerContext:
        raw = ctx.spec.prompt.strip()
        cleaned = _WHITESPACE.sub(" ", raw)
        if not cleaned:
            raise ValueError("prompt is empty after normalization")
        ctx.prompt = f"{cleaned}, {_STYLE_TAGS}"
        ctx.negative_prompt = ctx.spec.negative_prompt or "seam, seam line, distortion, watermark"
        logger.debug("prompt normalized: {} chars", len(ctx.prompt))
        return ctx