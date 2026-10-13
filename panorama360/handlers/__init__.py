from panorama360.handlers.base import BaseHandler, HandlerContext
from panorama360.handlers.prompt_handler import PromptHandler
from panorama360.handlers.reference_handler import ReferenceImageHandler
from panorama360.handlers.depth_handler import DepthHandler
from panorama360.handlers.cubemap_handler import CubemapSeedHandler

HANDLER_REGISTRY: dict[str, type[BaseHandler]] = {
    "prompt": PromptHandler,
    "reference": ReferenceImageHandler,
    "depth": DepthHandler,
    "cubemap_seed": CubemapSeedHandler,
}

__all__ = [
    "BaseHandler",
    "HandlerContext",
    "PromptHandler",
    "ReferenceImageHandler",
    "DepthHandler",
    "CubemapSeedHandler",
    "HANDLER_REGISTRY",
]