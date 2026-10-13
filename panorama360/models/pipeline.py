"""Pipeline and tiling configuration schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TileConfig(BaseModel):
    tile_w: int = Field(default=1024, ge=256, le=4096)
    tile_h: int = Field(default=1024, ge=256, le=4096)
    overlap: int = Field(default=96, ge=0, le=512)
    pole_overlap_boost: int = Field(default=48, ge=0, le=256)
    batch_size: int = Field(default=1, ge=1, le=16)


class PipelineConfig(BaseModel):
    """Top-level pipeline knobs. Loaded from TOML, overridable per-job."""

    base_model: str = "sdxl-panorama-v2"
    refine_model: str = "panorama-refiner-lora-v3"
    tile: TileConfig = Field(default_factory=TileConfig)
    seam_blend_px: int = Field(default=128, ge=16, le=512)
    depth_guided: bool = True
    depth_model: str = "depth-anything-v2-small"
    vae_tiling: bool = True
    attention_slicing: bool = True
    cpu_offload: bool = False
    dtype: str = Field(default="fp16", pattern="^(fp16|bf16|fp32)$")
    device: str = Field(default="cuda", pattern="^(cuda|cpu|mps)$")