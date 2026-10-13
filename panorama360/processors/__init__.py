from panorama360.processors.base import BaseProcessor
from panorama360.processors.diffusion_processor import DiffusionProcessor
from panorama360.processors.tiling_processor import TilingProcessor
from panorama360.processors.seam_processor import SeamProcessor
from panorama360.processors.depth_processor import DepthProcessor

PROCESSOR_REGISTRY: dict[str, type[BaseProcessor]] = {
    "diffusion": DiffusionProcessor,
    "tiling": TilingProcessor,
    "seam": SeamProcessor,
    "depth": DepthProcessor,
}

__all__ = [
    "BaseProcessor",
    "DiffusionProcessor",
    "TilingProcessor",
    "SeamProcessor",
    "DepthProcessor",
    "PROCESSOR_REGISTRY",
]