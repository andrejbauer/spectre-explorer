"""Assembling objects out of copies of other objects.

A grammar names some shapes and some rules.  A rule says what an object of one
generation is made of: a list of parts, each a copy of some object, placed by turning
it and then sliding it until one of its anchor points sits on an anchor point of a
part already placed.  Nothing is ever scaled; objects grow because they have more
parts.

That is enough to write down Kaplan's substitutions and Boris Horvat's mega-object
grammars in the same notation, and the result is an ordinary patch, so everything
that draws or measures a tiling works on it unchanged.

A grammar is plain data.  Write it as a Python dictionary or as JSON; the two have
the same shape, and `examples/` holds one of each.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from .geometry import (
    IDENTITY,
    Point,
    Transform,
    apply,
    compose,
    rotation,
    translation_from_to,
)
from .tiling import Node, Supertile, Tile

REFLECTION: Transform = (-1, 0, 0, 0, 1, 0)


@dataclass(frozen=True)
class Shape:
    """A drawn outline with anchor points on it."""

    outline: tuple[Point, ...]
    anchors: tuple[Point, ...]


@dataclass(frozen=True)
class Part:
    """One copy inside a rule.

    The copy is turned by `turn` degrees, reflected first if `reflect` is set, and
    then slid until its own anchor number `anchor` lands on anchor number `onto` of
    an earlier part.  That earlier part is the one before it unless `after` names
    another by position.  `generation` is a step relative to the object being built,
    so -1 means "one generation younger" and 0 means "the same generation".
    """

    symbol: str
    generation: int = -1
    turn: float = 0.0
    anchor: int = 0
    onto: int = 0
    after: int | None = None
    reflect: bool = False


@dataclass(frozen=True)
class Rule:
    """What an object is at generation zero, and what it is made of after that.

    Generation zero is the single shape named by `base`, unless `seed` gives parts to
    assemble instead, which is what an object needs when it does not start out as one
    piece.  A part may name a shape as well as another rule.
    """

    base: str = ""
    seed: tuple[Part, ...] = ()
    parts: tuple[Part, ...] = ()
    anchors: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True)
class Grammar:
    """A named collection of shapes and rules."""

    name: str
    shapes: dict[str, Shape]
    rules: dict[str, Rule]
    description: str = ""


def _points(raw: Sequence[Sequence[float]]) -> tuple[Point, ...]:
    return tuple((float(x), float(y)) for x, y in raw)


def read(source: dict[str, Any]) -> Grammar:
    """Read a grammar from a dictionary, as loaded from JSON or written by hand."""
    shapes = {
        name: Shape(_points(shape["outline"]), _points(shape.get("anchors", ())))
        for name, shape in source["shapes"].items()
    }
    rules = {
        name: Rule(
            base=rule.get("base", ""),
            seed=tuple(Part(**part) for part in rule.get("seed", ())),
            parts=tuple(Part(**part) for part in rule.get("parts", ())),
            anchors=tuple(
                (entry["part"], entry["anchor"]) for entry in rule.get("anchors", ())
            ),
        )
        for name, rule in source["rules"].items()
    }
    known = set(rules) | set(shapes)
    missing = {
        part.symbol
        for rule in rules.values()
        for part in rule.seed + rule.parts
        if part.symbol not in known
    } | {rule.base for rule in rules.values() if rule.base and rule.base not in shapes}
    empty = {name for name, rule in rules.items() if not rule.base and not rule.seed}
    if missing:
        raise ValueError(
            "the grammar refers to names it does not define: " + ", ".join(sorted(missing))
        )
    elif empty:
        raise ValueError(
            "these rules say nothing about generation zero, so they need a base shape "
            "or a seed: " + ", ".join(sorted(empty))
        )
    return Grammar(
        name=source.get("name", "grammar"),
        description=source.get("description", ""),
        shapes=shapes,
        rules=rules,
    )


def load(path: str | Path) -> Grammar:
    """Read a grammar from a JSON file."""
    return read(json.loads(Path(path).read_text(encoding="utf-8")))


def _turn(degrees: float, reflect: bool) -> Transform:
    radians = math.radians(degrees)
    turn = rotation(math.cos(radians), math.sin(radians))
    return compose(turn, REFLECTION) if reflect else turn


def build(grammar: Grammar, symbol: str, generation: int) -> Node:
    """The object a symbol stands for at a generation."""
    built: dict[tuple[str, int], Node] = {}
    building: set[tuple[str, int]] = set()

    def make(name: str, level: int) -> Node:
        wanted = (name, level)
        if wanted in built:
            return built[wanted]
        elif wanted in building:
            raise ValueError(
                f"{name} at generation {level} is defined in terms of itself"
            )
        elif name in grammar.shapes:
            shape = grammar.shapes[name]
            built[wanted] = Tile(name, shape.outline, shape.anchors)
            return built[wanted]
        else:
            building.add(wanted)
            rule = grammar.rules[name]
            built[wanted] = (
                _start(name, rule) if level <= 0 else _assemble(name, rule.parts, level)
            )
            building.discard(wanted)
            return built[wanted]

    def _start(name: str, rule: Rule) -> Node:
        if rule.seed:
            return _assemble(name, rule.seed, 0)
        else:
            shape = grammar.shapes[rule.base]
            return Tile(name, shape.outline, shape.anchors)

    def _assemble(name: str, parts: Sequence[Part], level: int) -> Node:
        rule = grammar.rules[name]
        placed: list[tuple[Node, Transform]] = []
        anchors: list[tuple[Point, ...]] = []
        for position, part in enumerate(parts):
            child = make(part.symbol, level + part.generation)
            turn = _turn(part.turn, part.reflect)
            if position == 0:
                transform = turn
            else:
                earlier = position - 1 if part.after is None else part.after
                transform = compose(
                    translation_from_to(
                        apply(turn, child.keys[part.anchor]),
                        anchors[earlier][part.onto],
                    ),
                    turn,
                )
            placed.append((child, transform))
            anchors.append(tuple(apply(transform, key) for key in child.keys))
        chosen = tuple(
            anchors[part][anchor]
            for part, anchor in rule.anchors
            if part < len(anchors) and anchor < len(anchors[part])
        )
        return Supertile(name, tuple(placed), chosen or anchors[0])

    return make(symbol, generation)


def counts(grammar: Grammar, generation: int) -> dict[str, int]:
    """How many base shapes each symbol stands for, at one generation.

    Comparing these with a sequence worked out by hand is the quickest way to tell
    whether a grammar says what its author meant.
    """
    from .tiling import tile_count

    return {
        symbol: tile_count(build(grammar, symbol, generation))
        for symbol in grammar.rules
    }
