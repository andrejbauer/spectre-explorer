"""The `spectre` command."""

from __future__ import annotations

import argparse
import gzip
import sys
from contextlib import contextmanager
from typing import IO, Iterator, Sequence

from . import data, svg
from .colors import BY_NAME
from .systems import SYSTEMS, grow, patch
from .tiling import Rectangle, bounds, tile_count

RASTER_SUFFIXES = (".png", ".pdf", ".jpg", ".jpeg", ".tif", ".tiff")


def _system_help() -> str:
    return "; ".join(f"{name} is {system.description}" for name, system in SYSTEMS.items())


@contextmanager
def _open_text(path: str | None) -> Iterator[IO[str]]:
    """Open a file for writing, compressing it when the name asks for that, or use
    standard output when no name is given."""
    if path is None:
        yield sys.stdout
    elif path.endswith(".svgz") or path.endswith(".gz"):
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            yield handle
    else:
        with open(path, "w", encoding="utf-8") as handle:
            yield handle


def _painting(arguments: argparse.Namespace):
    color_map = BY_NAME[arguments.colors]
    if arguments.color_by == "label":
        return color_map, svg.by_label(color_map)
    elif arguments.color_by.startswith("ancestor:"):
        return color_map, svg.by_ancestor(
            color_map, int(arguments.color_by.split(":", 1)[1])
        )
    else:
        raise SystemExit(
            f"unknown coloring {arguments.color_by!r}: "
            "use 'label' or 'ancestor:N' for a whole number N"
        )


def _window(arguments: argparse.Namespace) -> Rectangle | None:
    return None if arguments.window is None else tuple(arguments.window)


def _add_drawing_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--colors",
        default=None,
        choices=sorted(BY_NAME),
        help="color map (each system has its own default)",
    )
    parser.add_argument(
        "--color-by",
        default="label",
        metavar="RULE",
        help="'label' colors each tile by its own label; 'ancestor:N' colors it by "
        "the supertile N rounds above it, which shows the fractal structure",
    )
    parser.add_argument(
        "--mode",
        default="use",
        choices=("use", "flat", "nested"),
        help="SVG encoding: 'use' defines each outline once and places it by "
        "reference; 'flat' writes every coordinate out; 'nested' mirrors the "
        "substitution and stays small at any depth",
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=3,
        help="decimal places for coordinates, in tile units (default 3)",
    )
    parser.add_argument(
        "--stroke-width",
        type=float,
        default=0.02,
        help="outline width in tile units, so it does not change with depth",
    )
    parser.add_argument("--stroke", default="black", help="outline color")
    parser.add_argument(
        "--window",
        type=float,
        nargs=4,
        metavar=("LEFT", "BOTTOM", "RIGHT", "TOP"),
        help="draw only the tiles meeting this rectangle, in tile units",
    )
    parser.add_argument(
        "--width", type=int, default=1000, help="picture width in pixels"
    )


def _draw(arguments: argparse.Namespace) -> None:
    root = patch(arguments.system, arguments.category, arguments.generation)
    color_map, painting = _painting(arguments)
    window = _window(arguments)
    if arguments.out is not None and arguments.out.lower().endswith(RASTER_SUFFIXES):
        from . import raster

        count = raster.write(
            arguments.out,
            root,
            color_map=color_map,
            painting=painting,
            window=window,
            stroke_width=arguments.stroke_width,
            stroke=arguments.stroke,
            pixel_width=arguments.width,
        )
    else:
        with _open_text(arguments.out) as handle:
            count = svg.write(
                handle,
                root,
                mode=arguments.mode,
                color_map=color_map,
                painting=painting,
                precision=arguments.precision,
                stroke_width=arguments.stroke_width,
                stroke=arguments.stroke,
                window=window,
                pixel_width=arguments.width,
                title=f"{arguments.system} {arguments.category or ''} "
                f"generation {arguments.generation}".strip(),
            )
    print(f"{count} tiles written to {arguments.out or 'standard output'}", file=sys.stderr)


def _count(arguments: argparse.Namespace) -> None:
    system = SYSTEMS[arguments.system]
    print("generation," + ",".join(system.categories))
    tiles = system.start()
    for generation in range(arguments.through + 1):
        print(
            f"{generation},"
            + ",".join(str(tile_count(tiles[label])) for label in system.categories)
        )
        tiles = system.substitute(tiles)


def _data(arguments: argparse.Namespace) -> None:
    root = patch(arguments.system, arguments.category, arguments.generation)
    with _open_text(arguments.out) as handle:
        count = data.write(handle, root, window=_window(arguments))
    print(f"{count} rows written to {arguments.out or 'standard output'}", file=sys.stderr)


def _frames(arguments: argparse.Namespace) -> None:
    color_map, painting = _painting(arguments)
    window = _window(arguments)
    for generation in range(arguments.through + 1):
        root = patch(arguments.system, arguments.category, generation)
        path = arguments.pattern % generation
        with _open_text(path) as handle:
            count = svg.write(
                handle,
                root,
                mode=arguments.mode,
                color_map=color_map,
                painting=painting,
                precision=arguments.precision,
                stroke_width=arguments.stroke_width,
                stroke=arguments.stroke,
                window=window,
                pixel_width=arguments.width,
                title=f"generation {generation}",
            )
        print(f"{path}: {count} tiles", file=sys.stderr)


def _grammar_count(arguments: argparse.Namespace) -> None:
    from . import grammar

    rules = grammar.load(arguments.file)
    names = sorted(rules.rules)
    print("generation," + ",".join(names))
    for generation in range(arguments.through + 1):
        counted = grammar.counts(rules, generation)
        print(f"{generation}," + ",".join(str(counted[name]) for name in names))


def _grammar_draw(arguments: argparse.Namespace) -> None:
    from . import grammar
    from .colors import for_labels
    from .tiling import approximate, base_tiles

    rules = grammar.load(arguments.file)
    root = approximate(grammar.build(rules, arguments.symbol, arguments.generation))
    color_map = for_labels(list(base_tiles(root)) + list(rules.rules))
    painting = (
        svg.by_ancestor(color_map, int(arguments.color_by.split(":", 1)[1]))
        if arguments.color_by.startswith("ancestor:")
        else svg.by_label(color_map)
    )
    window = _window(arguments)
    if arguments.out is not None and arguments.out.lower().endswith(RASTER_SUFFIXES):
        from . import raster

        count = raster.write(
            arguments.out,
            root,
            color_map=color_map,
            painting=painting,
            window=window,
            stroke_width=arguments.stroke_width,
            stroke=arguments.stroke,
            pixel_width=arguments.width,
        )
    else:
        with _open_text(arguments.out) as handle:
            count = svg.write(
                handle,
                root,
                mode=arguments.mode,
                color_map=color_map,
                painting=painting,
                precision=arguments.precision,
                stroke_width=arguments.stroke_width,
                stroke=arguments.stroke,
                window=window,
                pixel_width=arguments.width,
                title=f"{rules.name}: {arguments.symbol} at generation "
                f"{arguments.generation}",
            )
    print(
        f"{count} pieces written to {arguments.out or 'standard output'}",
        file=sys.stderr,
    )


def _grammar_new(arguments: argparse.Namespace) -> None:
    from importlib.resources import files

    template = files("spectre_explorer").joinpath("template.json").read_text()
    with open(arguments.file, "w", encoding="utf-8") as handle:
        handle.write(template)
    print(f"a grammar to edit is in {arguments.file}", file=sys.stderr)


def _bounds(arguments: argparse.Namespace) -> None:
    root = patch(arguments.system, arguments.category, arguments.generation)
    left, bottom, right, top = bounds(root)
    print(f"{left:.4f} {bottom:.4f} {right:.4f} {top:.4f}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spectre",
        description="Generate, crop, color and measure aperiodic tilings built "
        "from the Spectre, the hat and the turtle.",
        epilog="Tilings: " + _system_help(),
    )
    commands = parser.add_subparsers(dest="command", required=True)

    def with_patch(name: str, help_text: str) -> argparse.ArgumentParser:
        sub = commands.add_parser(name, help=help_text, description=help_text)
        sub.add_argument("system", choices=sorted(SYSTEMS), help="which tiling")
        sub.add_argument(
            "--category",
            default=None,
            help="which labelled patch to draw (default depends on the tiling)",
        )
        return sub

    draw = with_patch("draw", "Draw a patch of a tiling to SVG, PNG or PDF.")
    draw.add_argument("--generation", "-g", type=int, required=True)
    draw.add_argument("--out", "-o", default=None, help="output file")
    _add_drawing_options(draw)
    draw.set_defaults(run=_draw)

    count = commands.add_parser(
        "count", help="Print the tile count of each category, generation by generation."
    )
    count.add_argument("system", choices=sorted(SYSTEMS))
    count.add_argument("--through", "-g", type=int, default=8)
    count.set_defaults(run=_count)

    table = with_patch("data", "Write one row per tile as CSV.")
    table.add_argument("--generation", "-g", type=int, required=True)
    table.add_argument("--out", "-o", default=None)
    table.add_argument(
        "--window", type=float, nargs=4, metavar=("LEFT", "BOTTOM", "RIGHT", "TOP")
    )
    table.set_defaults(run=_data)

    frames = with_patch("frames", "Draw one picture per generation, for an animation.")
    frames.add_argument("--through", "-g", type=int, required=True)
    frames.add_argument(
        "--pattern",
        default="frame-%02d.svg",
        help="output name with a %%d in it (default frame-%%02d.svg)",
    )
    _add_drawing_options(frames)
    frames.set_defaults(run=_frames)

    extent = with_patch("bounds", "Print the rectangle a patch occupies, in tile units.")
    extent.add_argument("--generation", "-g", type=int, required=True)
    extent.set_defaults(run=_bounds)

    grammar = commands.add_parser(
        "grammar",
        help="Work with a grammar of your own: rules that build objects out of "
        "copies of other objects.",
    )
    kinds = grammar.add_subparsers(dest="kind", required=True)

    started = kinds.add_parser("new", help="Write a grammar to start from.")
    started.add_argument("file", help="file to write")
    started.set_defaults(run=_grammar_new)

    counted = kinds.add_parser(
        "count", help="Print how many pieces each symbol stands for, generation by "
        "generation, which is the quickest check that a grammar says what you meant."
    )
    counted.add_argument("file")
    counted.add_argument("--through", "-g", type=int, default=6)
    counted.set_defaults(run=_grammar_count)

    drawn = kinds.add_parser("draw", help="Draw one symbol of a grammar.")
    drawn.add_argument("file")
    drawn.add_argument("--symbol", "-s", required=True, help="which rule to draw")
    drawn.add_argument("--generation", "-g", type=int, required=True)
    drawn.add_argument("--out", "-o", default=None)
    _add_drawing_options(drawn)
    drawn.set_defaults(run=_grammar_draw)

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if getattr(arguments, "colors", None) is None and hasattr(arguments, "system"):
        arguments.colors = SYSTEMS[arguments.system].default_colors
    arguments.run(arguments)
