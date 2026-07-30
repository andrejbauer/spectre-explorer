"""The `spectre` command."""

from __future__ import annotations

import csv
import gzip
import re

import pytest

from spectre_explorer.cli import main


def test_drawing_writes_an_svg(tmp_path):
    out = tmp_path / "patch.svg"
    main(["draw", "tile11", "-g", "3", "-o", str(out)])
    text = out.read_text()
    assert len(re.findall(r"<use ", text)) == 488


def test_a_compressed_name_gives_a_compressed_file(tmp_path):
    out = tmp_path / "patch.svgz"
    main(["draw", "tile11", "-g", "3", "-o", str(out)])
    assert len(re.findall(r"<use ", gzip.open(out, "rt").read())) == 488


def test_counting_prints_a_table(capsys):
    main(["count", "tile11", "--through", "4"])
    rows = list(csv.DictReader(capsys.readouterr().out.splitlines()))
    assert [row["Gamma"] for row in rows] == ["2", "8", "62", "488", "3842"]


def test_the_hat_counts_are_fibonacci_and_lucas(capsys):
    main(["count", "hat", "--through", "5"])
    rows = list(csv.DictReader(capsys.readouterr().out.splitlines()))
    assert [row["H8"] for row in rows] == ["1", "8", "55", "377", "2584", "17711"]
    assert [row["H7"] for row in rows] == ["2", "7", "47", "322", "2207", "15127"]


def test_the_table_has_one_row_for_each_tile(tmp_path):
    out = tmp_path / "tiles.csv"
    main(["data", "tile11", "-g", "3", "-o", str(out)])
    rows = list(csv.DictReader(out.read_text().splitlines()))
    assert len(rows) == 488
    assert rows[0]["ancestry"].startswith("Gamma/")
    assert rows[0]["label"] in ("Gamma1", "Gamma2", "Delta", "Pi", "Theta")


def test_frames_are_numbered(tmp_path):
    main(
        [
            "frames",
            "tile11",
            "-g",
            "2",
            "--pattern",
            str(tmp_path / "frame-%02d.svg"),
        ]
    )
    assert sorted(path.name for path in tmp_path.glob("*.svg")) == [
        "frame-00.svg",
        "frame-01.svg",
        "frame-02.svg",
    ]


def test_a_window_shrinks_the_output(tmp_path):
    whole = tmp_path / "whole.svg"
    part = tmp_path / "part.svg"
    main(["draw", "tile11", "-g", "5", "-o", str(whole)])
    main(["draw", "tile11", "-g", "5", "--window", "-10", "-10", "10", "10", "-o", str(part)])
    assert part.stat().st_size < whole.stat().st_size / 10


def test_an_unknown_coloring_is_refused(tmp_path):
    with pytest.raises(SystemExit):
        main(["draw", "tile11", "-g", "1", "--color-by", "sideways", "-o", str(tmp_path / "x.svg")])
