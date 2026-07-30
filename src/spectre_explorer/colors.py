"""Color maps, ported from the reference implementations.

A color map sends a tile label to a red-green-blue triple.  The Spectre maps use
the nine substitution labels, splitting `Gamma` into the two halves of the mystic;
the Hat map uses the three labels of the H7/H8 system.
"""

from __future__ import annotations

Color = tuple[int, int, int]
ColorMap = dict[str, Color]

FIGURE_53: ColorMap = {
    "Gamma": (203, 157, 126),
    "Gamma1": (203, 157, 126),
    "Gamma2": (203, 157, 126),
    "Delta": (163, 150, 133),
    "Theta": (208, 215, 150),
    "Lambda": (184, 205, 178),
    "Xi": (211, 177, 144),
    "Pi": (218, 197, 161),
    "Sigma": (191, 146, 126),
    "Phi": (228, 213, 167),
    "Psi": (224, 223, 156),
}

BRIGHT: ColorMap = {
    "Gamma": (255, 255, 255),
    "Gamma1": (255, 255, 255),
    "Gamma2": (255, 255, 255),
    "Delta": (220, 220, 220),
    "Theta": (255, 191, 191),
    "Lambda": (255, 160, 122),
    "Xi": (255, 242, 0),
    "Pi": (135, 206, 250),
    "Sigma": (245, 245, 220),
    "Phi": (0, 255, 0),
    "Psi": (0, 255, 255),
}

MYSTICS: ColorMap = {
    "Gamma": (196, 201, 169),
    "Gamma1": (196, 201, 169),
    "Gamma2": (156, 160, 116),
    "Delta": (247, 252, 248),
    "Theta": (247, 252, 248),
    "Lambda": (247, 252, 248),
    "Xi": (247, 252, 248),
    "Pi": (247, 252, 248),
    "Sigma": (247, 252, 248),
    "Phi": (247, 252, 248),
    "Psi": (247, 252, 248),
}

PRIDE: ColorMap = {
    "Gamma": (255, 255, 255),
    "Gamma1": (97, 57, 21),
    "Gamma2": (0, 0, 0),
    "Delta": (2, 129, 33),
    "Theta": (0, 76, 255),
    "Lambda": (118, 0, 136),
    "Xi": (229, 0, 0),
    "Pi": (255, 175, 199),
    "Sigma": (115, 215, 238),
    "Phi": (255, 141, 0),
    "Psi": (255, 238, 0),
}

GRAY: ColorMap = {
    "single": (255, 255, 255),
    "unflipped": (200, 200, 200),
    "flipped": (150, 150, 150),
}

BY_NAME: dict[str, ColorMap] = {
    "pride": PRIDE,
    "mystics": MYSTICS,
    "fig53": FIGURE_53,
    "bright": BRIGHT,
    "gray": GRAY,
}

FALLBACK: Color = (200, 200, 200)

#: A readable spread of hues for labels that no map names, as in a grammar the user
#: has just written.
PALETTE: tuple[Color, ...] = (
    (68, 119, 170),
    (238, 119, 51),
    (34, 136, 51),
    (204, 51, 17),
    (170, 51, 119),
    (0, 153, 136),
    (238, 187, 34),
    (136, 34, 85),
)


def for_labels(labels: list[str]) -> ColorMap:
    """A color map covering whatever labels are in hand."""
    return {
        label: PALETTE[index % len(PALETTE)]
        for index, label in enumerate(sorted(labels))
    }


def color_of(color_map: ColorMap, label: str) -> Color:
    """The color of a label, or a neutral gray for a label the map does not name."""
    return color_map.get(label, FALLBACK)


def to_css(color: Color) -> str:
    """A color written the way SVG wants it."""
    return f"rgb({color[0]},{color[1]},{color[2]})"
