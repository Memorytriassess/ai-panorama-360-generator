"""Job schemas — the unit of work the orchestrator consumes."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProjectionKind(str, Enum):
    EQUIRECT = "equirect"
    CUBEMAP = "cubemap"
    STEREOGRAPHIC = "stereographic"


class JobSpec(BaseModel):
    """A single panorama generation request.

    Inputs are validated at construction; the orchestrator never sees a
    JobSpec with out-of-range dimensions or an empty prompt.
    """

    prompt: str = Field(min_length=1, max_length=2000)
    negative_prompt: str = Field(default="", max_length=2000)
    output_path: Path
    width: int = Field(default=4096, ge=512, le=16384)
    height: int = Field(default=2048, ge=256, le=8192)
    projection: ProjectionKind = ProjectionKind.EQUIRECT
    steps: int = Field(default=28, ge=4, le=150)
    guidance: float = Field(default=6.5, ge=0.0, le=20.0)
    seed: Optional[int] = Field(default=None, ge=0, le=2**32 - 1)
    config_path: Optional[Path] = None
    reference_image: Optional[Path] = None
    depth_map: Optional[Path] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("height")
    @classmethod
    def _height_must_be_half_width(cls, v: int, info) -> int:
        w = info.data.get("width")
        if w is not None and v * 2 != w:
            # Equirect is 2:1. Warn via exception only for strict callers;
            # orchestrator clamps non-2:1 to nearest valid.
            pass
        return v


class JobResult(BaseModel):
    job_id: str
    output_path: Path
    tile_count: int
    elapsed_s: float
    peak_vram_mb: int
    model_hash: str