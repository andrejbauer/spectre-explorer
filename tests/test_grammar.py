"""Grammars written as data."""

from __future__ import annotations

from pathlib import Path

import pytest

from spectre_explorer import grammar
from spectre_explorer.tiling import tile_count

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"

SQUARE = {
    "shapes": {
        "block": {
            "outline": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "anchors": [[0, 0], [1, 0], [1, 1], [0, 1]],
        }
    },
    "rules": {
        "A": {
            "base": "block",
            "parts": [
                {"symbol": "A", "generation": -1},
                {"symbol": "A", "generation": -1, "onto": 1, "after": 0},
            ],
            "anchors": [
                {"part": 0, "anchor": 0},
                {"part": 1, "anchor": 1},
                {"part": 1, "anchor": 2},
                {"part": 0, "anchor": 3},
            ],
        }
    },
}


def test_a_rule_doubles_what_it_names_twice():
    rules = grammar.read(SQUARE)
    assert [tile_count(grammar.build(rules, "A", n)) for n in range(5)] == [
        1,
        2,
        4,
        8,
        16,
    ]


def test_parts_are_placed_where_the_anchors_say():
    rules = grammar.read(SQUARE)
    from spectre_explorer.geometry import apply
    from spectre_explorer.tiling import placements

    corners = {
        tuple(round(value, 6) for value in apply(place.transform, (0.0, 0.0)))
        for place in placements(grammar.build(rules, "A", 2))
    }
    assert corners == {(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)}


def test_a_rule_may_start_as_more_than_one_piece():
    spec = {
        "shapes": SQUARE["shapes"],
        "rules": {
            "P": {
                "seed": [
                    {"symbol": "block"},
                    {"symbol": "block", "onto": 1, "after": 0},
                ],
                "parts": [{"symbol": "P", "generation": -1}],
            }
        },
    }
    rules = grammar.read(spec)
    assert tile_count(grammar.build(rules, "P", 0)) == 2
    assert tile_count(grammar.build(rules, "P", 3)) == 2


def test_a_grammar_that_names_what_it_has_not_defined_is_refused():
    with pytest.raises(ValueError, match="does not define"):
        grammar.read(
            {"shapes": {}, "rules": {"A": {"base": "nothing", "parts": []}}}
        )


def test_a_rule_with_no_beginning_is_refused():
    with pytest.raises(ValueError, match="generation zero"):
        grammar.read({"shapes": {}, "rules": {"A": {"parts": []}}})


def test_a_rule_that_needs_itself_at_its_own_generation_is_refused():
    spec = {
        "shapes": SQUARE["shapes"],
        "rules": {
            "A": {"base": "block", "parts": [{"symbol": "A", "generation": 0}]}
        },
    }
    with pytest.raises(ValueError, match="defined in terms of itself"):
        grammar.build(grammar.read(spec), "A", 2)


def test_the_shipped_template_works():
    from importlib.resources import files

    text = files("spectre_explorer").joinpath("template.json").read_text()
    import json

    rules = grammar.read(json.loads(text))
    assert tile_count(grammar.build(rules, "A", 3)) == 27


def test_the_mega_object_grammar_gives_boris_horvats_counts():
    """MA 1, 4, 25, 136 and MC 1, 7, 37 and PA 2, 10, 60, 332 are the numbers in the
    names of the figures on his own pages, so the counting in the grammar is his.
    The placement of the parts is not, and is a first fit only."""
    rules = grammar.load(EXAMPLES / "spectre-mega-objects.json")
    counted = [grammar.counts(rules, n) for n in range(4)]
    assert [entry["MA"] for entry in counted] == [1, 4, 25, 136]
    assert [entry["MC"] for entry in counted][:3] == [1, 7, 37]
    assert [entry["PA"] for entry in counted] == [2, 10, 60, 332]
