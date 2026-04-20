"""Tests for fontpair analyzer."""

from __future__ import annotations

from pathlib import Path

import pytest

from fontpair.analyzer import analyze_font_info, compute_metrics
from fontpair.models import FontMetrics

FIXTURES = Path(__file__).parent / "fixtures" / "test_fonts"

FONT_FILES = list(FIXTURES.glob("*.ttf"))


@pytest.fixture(params=FONT_FILES, ids=[f.name for f in FONT_FILES])
def font_file(request) -> Path:
    return request.param


def test_compute_metrics_returns_metrics(font_file: Path) -> None:
    metrics = compute_metrics(font_file)
    assert isinstance(metrics, FontMetrics)
    assert 0.0 <= metrics.x_height_ratio <= 1.0
    assert 100 <= metrics.weight <= 900
    assert metrics.avg_width > 0
    assert metrics.contrast >= 0.0


def test_metrics_weight_matches_file(font_file: Path) -> None:
    metrics = compute_metrics(font_file)
    assert metrics.weight >= 100


def test_metrics_avg_width_reasonable(font_file: Path) -> None:
    metrics = compute_metrics(font_file)
    assert 100 <= metrics.avg_width <= 2000


def test_analyze_font_info_returns_details(font_file: Path) -> None:
    info = analyze_font_info(font_file)
    assert info["glyph_count"] > 0
    assert info["units_per_em"] > 0


def test_compute_metrics_nonexistent_file() -> None:
    with pytest.raises(Exception):
        compute_metrics(Path("/nonexistent/font.ttf"))
