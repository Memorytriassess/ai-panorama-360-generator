"""In-memory panorama and tile grid representations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray

FloatImage = NDArray[np.float32]  # HxWx3, range [0, 1]


@dataclass(slots=True)
class TileGrid:
    """A grid of overlapping tiles covering an equirect canvas.

    `overlap` is measured in pixels on each edge. Tiles at the poles use
    a wider vertical overlap to hide the singularity.
    """

    cols: int
    rows: int
    tile_w: int
    tile_h: int
    overlap: int = 96

    @property
    def total(self) -> int:
        return self.cols * self.rows

    def tile_origin(self, col: int, row: int) -> tuple[int, int]:
        x = col * (self.tile_w - self.overlap)
        y = row * (self.tile_h - self.overlap)
        return x, y


@dataclass(slots=True)
class PanoramaTensor:
    """A panorama in memory, plus provenance for the output driver."""

    image: FloatImage
    projection: Literal["equirect", "cubemap", "stereographic"] = "equirect"
    grid: TileGrid | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def shape(self) -> tuple[int, int, int]:
        return self.image.shape  # type: ignore[return-value]