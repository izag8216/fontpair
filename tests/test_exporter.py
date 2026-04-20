"""Tests for fontpair exporter."""

from __future__ import annotations

from pathlib import Path

import json

import pytest

from fontpair.exporter import export, export_css, export_json, export_yaml
from fontpair.models import FontCategory, FontInfo, FontMetrics, FontPair, ScoreBreakdown


def _pair() -> FontPair:
    heading = FontInfo(
        family="Playfair Display",
        style="Bold",
        weight=700,
        width=5,
        file_path=Path("/tmp/playfair.ttf"),
        category=FontCategory.SERIF,
        metrics=FontMetrics(x_height_ratio=0.48, weight=700, avg_width=520.0, contrast=0.15),
    )
    body = FontInfo(
        family="Inter",
        style="Regular",
        weight=400,
        width=5,
        file_path=Path("/tmp/inter.ttf"),
        category=FontCategory.SANS_SERIF,
        metrics=FontMetrics(x_height_ratio=0.52, weight=400, avg_width=480.0, contrast=0.08),
    )
    mono = FontInfo(
        family="Fira Code",
        style="Regular",
        weight=400,
        width=5,
        file_path=Path("/tmp/fira.ttf"),
        category=FontCategory.MONOSPACE,
        metrics=FontMetrics(x_height_ratio=0.50, weight=400, avg_width=600.0, contrast=0.05),
    )
    score = ScoreBreakdown(visual_harmony=90, readability=85, contrast_balance=80, x_height_compat=88, total=86.0)
    return FontPair(heading=heading, body=body, mono=mono, score=score, style_description="Modern classic")


def test_export_css() -> None:
    pairing = _pair()
    css = export_css(pairing)
    assert "--font-heading" in css
    assert "--font-body" in css
    assert "--font-mono" in css
    assert "Playfair Display" in css
    assert "Inter" in css
    assert "Fira Code" in css
    assert "font-family: var(--font-heading)" in css


def test_export_css_no_mono() -> None:
    pairing = _pair()
    no_mono = FontPair(heading=pairing.heading, body=pairing.body, mono=None, score=pairing.score)
    css = export_css(no_mono)
    assert "--font-mono" not in css


def test_export_json() -> None:
    pairing = _pair()
    raw = export_json(pairing)
    data = json.loads(raw)
    assert data["heading"]["family"] == "Playfair Display"
    assert data["body"]["family"] == "Inter"
    assert data["mono"]["family"] == "Fira Code"
    assert data["score"]["total"] == 86.0


def test_export_yaml() -> None:
    pairing = _pair()
    yaml_str = export_yaml(pairing)
    assert "heading:" in yaml_str
    assert "body:" in yaml_str
    assert "Playfair Display" in yaml_str


def test_export_format_dispatch() -> None:
    pairing = _pair()
    css = export(pairing, fmt="css")
    assert "--font-heading" in css
    json_str = export(pairing, fmt="json")
    assert json.loads(json_str)
    yaml_str = export(pairing, fmt="yaml")
    assert "heading:" in yaml_str


def test_export_unsupported_format() -> None:
    pairing = _pair()
    with pytest.raises(ValueError, match="Unsupported format"):
        export(pairing, fmt="xml")


def test_css_escaping() -> None:
    heading = FontInfo(
        family="Font With Spaces",
        style="Regular",
        weight=400,
        width=5,
        file_path=Path("/tmp/font.ttf"),
        category=FontCategory.SANS_SERIF,
    )
    body = FontInfo(
        family="Another Font",
        style="Regular",
        weight=400,
        width=5,
        file_path=Path("/tmp/body.ttf"),
        category=FontCategory.SANS_SERIF,
    )
    pair = FontPair(heading=heading, body=body)
    css = export_css(pair)
    assert '"Font With Spaces"' in css
