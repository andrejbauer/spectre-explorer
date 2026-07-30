"""Drawing a tiling straight to PNG or PDF with matplotlib.

Kept apart from the rest of the package so that the core needs nothing installed.
Import this only when a raster picture is wanted.
"""

from __future__ import annotations

from .colors import ColorMap
from .geometry import IDENTITY, apply, point_to_float
from .svg import Painting, by_label
from .tiling import Node, Rectangle, base_tiles, bounds, placements


def _outline(tile, transform) -> tuple[list[tuple[float, float]], list[int] | None]:
    """The vertices of a placed tile, with matplotlib path codes when it is curved."""
    from matplotlib.path import Path

    if tile.curve is None:
        return (
            [point_to_float(apply(transform, point)) for point in tile.outline],
            None,
        )
    else:
        points = [point_to_float(apply(transform, point)) for point in tile.curve]
        codes = [Path.MOVETO] + [Path.CURVE4] * (len(points) - 1)
        return points, codes


def write(
    path: str,
    root: Node,
    *,
    color_map: ColorMap,
    painting: Painting | None = None,
    window: Rectangle | None = None,
    stroke_width: float = 0.02,
    stroke: str = "black",
    pixel_width: int = 1000,
    dots_per_inch: int = 100,
    margin: float = 1.0,
) -> int:
    """Draw the tiling to a raster or vector file chosen by the extension."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as pyplot
    from matplotlib.collections import PathCollection
    from matplotlib.path import Path

    painted = by_label(color_map) if painting is None else painting
    left, bottom, right, top = window if window is not None else bounds(root)
    view = (left - margin, bottom - margin, right + margin, top + margin)
    width = view[2] - view[0]
    height = view[3] - view[1]

    shapes = base_tiles(root)
    paths = []
    fills = []
    for placement in placements(root, IDENTITY, window):
        points, codes = _outline(shapes[placement.label], placement.transform)
        paths.append(Path(points, codes, closed=True))
        red, green, blue = painted.color(placement)
        fills.append((red / 255, green / 255, blue / 255))

    figure = pyplot.figure(
        figsize=(pixel_width / dots_per_inch, pixel_width * height / width / dots_per_inch),
        dpi=dots_per_inch,
    )
    axes = figure.add_axes((0, 0, 1, 1))
    axes.set_xlim(view[0], view[2])
    axes.set_ylim(view[1], view[3])
    axes.set_aspect("equal")
    axes.axis("off")
    axes.add_collection(
        PathCollection(
            paths,
            facecolors=fills,
            edgecolors=stroke,
            linewidths=stroke_width * pixel_width / width * 72 / dots_per_inch,
            joinstyle="round",
        )
    )
    figure.savefig(path, dpi=dots_per_inch)
    pyplot.close(figure)
    return len(paths)
