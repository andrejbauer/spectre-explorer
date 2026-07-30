"""Writing a tiling as a table.

One row per tile, with enough in it to redraw the tile, to sort tiles by position,
and to tell which supertile each one came from.  Spreadsheets and statistics
packages read this directly, which beats reading it out of a picture.
"""

from __future__ import annotations

import csv
from typing import IO

from .geometry import IDENTITY, apply, point_to_float
from .tiling import Node, Rectangle, base_tiles, placements

COLUMNS = (
    "label",
    "ancestry",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "center_x",
    "center_y",
)


def write(
    stream: IO[str],
    root: Node,
    *,
    window: Rectangle | None = None,
    precision: int = 6,
) -> int:
    """Write one row per tile and return how many there were.

    The six numbers `a` to `f` are the tile's transform, meaning the map
    `(x, y) |-> (a x + b y + c, d x + e y + f)` applied to the outline of the tile
    named in `label`.  `ancestry` lists the labels from the whole patch down to the
    tile, separated by slashes.
    """
    shapes = base_tiles(root)
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(COLUMNS)
    count = 0
    for placement in placements(root, IDENTITY, window):
        outline = [
            point_to_float(apply(placement.transform, vertex))
            for vertex in shapes[placement.label].outline
        ]
        center = (
            sum(x for x, _ in outline) / len(outline),
            sum(y for _, y in outline) / len(outline),
        )
        writer.writerow(
            (
                placement.label,
                "/".join(placement.ancestry),
                *(round(float(entry), precision) for entry in placement.transform),
                round(center[0], precision),
                round(center[1], precision),
            )
        )
        count += 1
    return count
