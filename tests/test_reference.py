"""Agreement with the reference implementations.

The three sample files exported from Kaplan's Spectre app, and Boris Horvat's
exports from the H7/H8 app, are the only independent record of what these tilings
look like.  A wrong turn angle or a mirrored tile reproduces the tile counts exactly,
so counts alone prove nothing; these tests compare coordinates.

The samples are not part of the repository.  Point `SPECTRE_SAMPLES` at a directory
holding them, or set the environment variable `SPECTRE_SAMPLES`, and the tests run;
otherwise they skip.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from agreement import deviation, read_polygons, scale_between
from spectre_explorer.geometry import apply, point_to_float
from spectre_explorer.systems import patch
from spectre_explorer.tiling import base_tiles, placements

SAMPLES = Path(
    os.environ.get("SPECTRE_SAMPLES", Path(__file__).resolve().parents[2])
)

SPECTRE_FILES = {
    2: "spectre-gamma-round-2-tiles-62.svg",
    4: "spectre-gamma-round-4-tiles-3842.svg",
}

HAT_FILES = {
    ("H8", 3): "HAT-H8-GEN-3.svg",
    ("H7", 3): "HAT-H7-GEN-3.svg",
}


def outlines(system: str, category: str, generation: int):
    root = patch(system, category, generation)
    shapes = base_tiles(root)
    return [
        tuple(
            complex(*point_to_float(apply(place.transform, vertex)))
            for vertex in shapes[place.label].outline
        )
        for place in placements(root)
    ]


def sample(name: str):
    path = SAMPLES / name
    if not path.exists():
        pytest.skip(f"{path} is not here; see the note at the top of this file")
    return read_polygons(path.read_text())


@pytest.mark.parametrize("generation,name", SPECTRE_FILES.items())
def test_the_spectre_matches_the_reference_export(generation, name):
    theirs = sample(name)
    mine = outlines("tile11", "Gamma", generation)
    assert len(mine) == len(theirs)
    worst = deviation(mine, theirs)
    assert worst is not None, "the two are not the same tiling"
    assert worst / scale_between(mine, theirs) < 1e-9


@pytest.mark.parametrize("key,name", HAT_FILES.items())
def test_the_hat_matches_the_reference_export(key, name):
    category, generation = key
    theirs = sample(name)
    mine = outlines("hat", category, generation)
    assert len(mine) == len(theirs)
    worst = deviation(mine, theirs)
    assert worst is not None, "the two are not the same tiling"
    assert worst / scale_between(mine, theirs) < 1e-9


def test_the_turtle_is_not_the_hat():
    """Guards against the two shapes of the H7/H8 continuum being confused."""
    theirs = sample(HAT_FILES[("H8", 3)])
    assert deviation(outlines("turtle", "H8", 3), theirs) is None
