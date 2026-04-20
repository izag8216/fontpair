"""Tests for fontpair CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from fontpair.cli import cli
from fontpair.models import FontCategory, FontInfo, FontMetrics

FIXTURES = Path(__file__).parent / "fixtures" / "test_fonts"


def _mock_fonts():
    return [
        FontInfo(
            family="Roboto Slab",
            style="Regular",
            weight=400,
            width=5,
            file_path=FIXTURES / "RobotoSlab.ttf",
            category=FontCategory.SERIF,
            metrics=FontMetrics(x_height_ratio=0.48, weight=400, avg_width=520.0, contrast=0.12),
        ),
        FontInfo(
            family="Raleway",
            style="Regular",
            weight=400,
            width=5,
            file_path=FIXTURES / "Raleway.ttf",
            category=FontCategory.SANS_SERIF,
            metrics=FontMetrics(x_height_ratio=0.52, weight=400, avg_width=480.0, contrast=0.08),
        ),
        FontInfo(
            family="Roboto Mono",
            style="Regular",
            weight=400,
            width=5,
            file_path=FIXTURES / "RobotoMono.ttf",
            category=FontCategory.MONOSPACE,
            metrics=FontMetrics(x_height_ratio=0.50, weight=400, avg_width=600.0, contrast=0.05),
        ),
    ]


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "fontpair" in result.output


def test_scan_directory() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "--dir", str(FIXTURES)])
    assert result.exit_code == 0
    assert "Found" in result.output
    assert "fonts" in result.output


@patch("fontpair.cli.load_fonts")
@patch("fontpair.cli.get_connection")
def test_recommend_with_mock(conn_mock, load_mock) -> None:
    import sqlite3
    conn_mock.return_value = sqlite3.connect(":memory:")
    load_mock.return_value = _mock_fonts()

    runner = CliRunner()
    result = runner.invoke(cli, ["recommend", "--style", "modern", "--count", "3"])
    assert result.exit_code == 0


@patch("fontpair.cli.load_fonts")
@patch("fontpair.cli.get_connection")
def test_recommend_empty(conn_mock, load_mock) -> None:
    import sqlite3
    conn_mock.return_value = sqlite3.connect(":memory:")
    load_mock.return_value = []

    runner = CliRunner()
    result = runner.invoke(cli, ["recommend"])
    assert result.exit_code == 0 or "No fonts" in result.output


@patch("fontpair.cli.load_fonts")
@patch("fontpair.cli.get_connection")
def test_info_found(conn_mock, load_mock) -> None:
    import sqlite3
    conn_mock.return_value = sqlite3.connect(":memory:")
    load_mock.return_value = _mock_fonts()

    runner = CliRunner()
    result = runner.invoke(cli, ["info", "Raleway"])
    assert result.exit_code == 0
    assert "Raleway" in result.output


def test_info_missing_font() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["info", "NonExistentFont12345"])
    assert result.exit_code == 1 or "No fonts" in result.output


def test_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "scan" in result.output
    assert "recommend" in result.output
    assert "export" in result.output
    assert "info" in result.output
