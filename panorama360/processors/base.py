"""Base class for pipeline processors.

Processors run after handlers. They consume a `HandlerContext` and
produce a `PanoramaTensor` on the context, or refine an existing one.
Each processor declares its `requires` and `provides` keys so the
orchestrator can topologically order them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from panorama360.handlers.base import HandlerContext
from panorama360.models.panorama import PanoramaTensor


class BaseProcessor(ABC):
    name: str = "processor"
    requires: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()

    @abstractmethod
    async def process(self, ctx: HandlerContext) -> PanoramaTensor:
        """Return the panorama state after this stage."""
        raise NotImplementedError

    def _device(self, ctx: HandlerContext) -> str:
        return ctx.config.device