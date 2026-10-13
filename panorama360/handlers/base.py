"""Base class for ingest handlers.

Handlers run first in the pipeline. They normalize inputs into a
`HandlerContext` that processors consume. A handler must be pure with
respect to the context it receives — no global state, no side effects
beyond writing into the context.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from panorama360.models.job import JobSpec
from panorama360.models.pipeline import PipelineConfig


@dataclass
class HandlerContext:
    spec: JobSpec
    config: PipelineConfig
    prompt: str = ""
    negative_prompt: str = ""
    reference: NDArray[np.float32] | None = None
    depth: NDArray[np.float32] | None = None
    seed_latents: Any = None
    scratch: dict[str, Any] = field(default_factory=dict)

    def require_reference(self) -> NDArray[np.float32]:
        if self.reference is None:
            raise RuntimeError("reference image missing — run ReferenceImageHandler first")
        return self.reference


class BaseHandler(ABC):
    """A single ingest stage. `name` is used for logging and registry keys."""

    name: str = "handler"

    @abstractmethod
    async def handle(self, ctx: HandlerContext) -> HandlerContext:
        """Mutate and return the context. Must be idempotent for a given input."""
        raise NotImplementedError

    def _resolve(self, p: Path) -> Path:
        return p if p.is_absolute() else (Path.cwd() / p).resolve()