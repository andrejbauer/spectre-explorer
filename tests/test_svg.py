"""The SVG back end."""

from __future__ import annotations

import io
import re

import pytest

from agreement import deviation, expand_uses
from spectre_explorer import svg
from spectre_explorer.colors import BY_NAME
from spectre_explorer.geometry import apply, point_to_float
from spectre_explorer.systems import patch
from spectre_explorer.tiling import base_tiles, placements, tile_count


def render(root, **options) -> tuple[str, int]:
    stream = io.StringIO()
    count = svg.write(stream, root, color_map=BY_NAME["mystics"], **options)
    return stream.getvalue(), count


def outlines(root):
    shapes = base_tiles(root)
    return [
        tuple(
            complex(*point_to_float(apply(place.transform, vertex)))
            for vertex in shapes[place.label].outline
        )
        for place in placements(root)
    ]


@pytest.mark.parametrize("mode", ("use", "flat", "nested"))
def test_every_mode_writes_every_tile(mode):
    root = patch("tile11", "Gamma", 3)
    text, count = render(root, mode=mode)
    assert count == tile_count(root) == 488
    assert text.startswith("<?xml")
    assert text.rstrip().endswith("</svg>")


def test_the_stroke_attribute_is_the_one_svg_understands():
    """The reference exporters write `stroke-weight`, which is a p5 function name and
    not an SVG attribute, so their outlines silently fall back to one pixel."""
    text, _ = render(patch("tile11", "Gamma", 2))
    assert "stroke-width" in text
    assert "stroke-weight" not in text


def test_the_outline_is_defined_once_and_placed_by_reference():
    text, count = render(patch("tile11", "Gamma", 4), mode="use")
    assert len(re.findall(r"<polygon id=", text)) <= 4
    assert len(re.findall(r"<use ", text)) == count


def test_referring_beats_repeating_and_sharing_beats_both():
    root = patch("tile11", "Gamma", 4)
    sizes = {mode: len(render(root, mode=mode)[0]) for mode in ("use", "flat", "nested")}
    assert sizes["use"] < sizes["flat"] / 3
    assert sizes["nested"] < sizes["use"] / 10


def test_coordinates_do_not_shrink_as_the_patch_deepens():
    """The reference export bakes the zoom into every coordinate, so the digits
    needed grow with the generation.  Here the zoom lives in the viewBox."""
    shallow, _ = render(patch("tile11", "Gamma", 2), mode="use")
    deep, _ = render(patch("tile11", "Gamma", 5), mode="use")
    first = lambda text: re.search(r'<polygon id="[^"]+" points="([^"]+)"', text).group(1)
    assert first(shallow) == first(deep)


@pytest.mark.parametrize("precision,tolerance", ((6, 1e-5), (3, 1e-2), (1, 0.5)))
def test_rounding_stays_within_the_precision_asked_for(precision, tolerance):
    root = patch("tile11", "Gamma", 3)
    text, _ = render(root, mode="use", precision=precision)
    worst = deviation(expand_uses(text), outlines(root))
    assert worst is not None
    assert worst < tolerance


def test_a_window_keeps_only_the_tiles_that_meet_it():
    root = patch("tile11", "Gamma", 5)
    _, whole = render(root)
    _, cropped = render(root, window=(-10.0, -10.0, 10.0, 10.0))
    assert 0 < cropped < whole


def test_the_curved_spectre_is_written_as_curves():
    text, _ = render(patch("spectre", "Gamma", 1), mode="use")
    assert "<path" in text
    assert "C " in text
