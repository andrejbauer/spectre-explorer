"""Spectre explorer: aperiodic tilings built from the Spectre, the hat and the turtle.

The short way in:

    from spectre_explorer import tiling_patch, draw

    patch = tiling_patch("tile11", category="Gamma", generation=5)
    draw(patch, "patch.svg")

`tiling_patch` grows a patch, `draw` writes a picture of it, and `table` writes one
row per tile.  Everything they use is available separately: `systems` lists the
tilings, `tiling.placements` walks a patch tile by tile, and `svg`, `raster` and
`data` are the three back ends.
"""

from __future__ import annotations

from .colors import BY_NAME as COLOR_MAPS
from .systems import SYSTEMS, grow, patch as tiling_patch
from .tiling import Node, Placement, Rectangle, bounds, placements, tile_count

__all__ = [
    "COLOR_MAPS",
    "Node",
    "Placement",
    "Rectangle",
    "SYSTEMS",
    "bounds",
    "draw",
    "grow",
    "placements",
    "table",
    "tile_count",
    "tiling_patch",
]

__version__ = "0.1.0"


def draw(root: Node, path: str, *, colors: str = "mystics", **options) -> int:
    """Write a picture of a patch, choosing the format from the file name."""
    from . import data, raster, svg

    color_map = COLOR_MAPS[colors]
    if path.lower().endswith((".png", ".pdf", ".jpg", ".jpeg", ".tif", ".tiff")):
        return raster.write(path, root, color_map=color_map, **options)
    else:
        import gzip

        opener = gzip.open if path.endswith((".svgz", ".gz")) else open
        with opener(path, "wt", encoding="utf-8") as handle:
            return svg.write(handle, root, color_map=color_map, **options)


def table(root: Node, path: str, **options) -> int:
    """Write one row per tile of a patch as CSV."""
    from . import data

    with open(path, "w", encoding="utf-8") as handle:
        return data.write(handle, root, **options)
