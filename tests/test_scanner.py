"""Tests for fontpair scanner."""

from __future__ import annotations

from pathlib import Path

import pytest

from fontpair.models import FontCategory, ScanResult
from fontpair.scanner import scan_directory

FIXTURES = Path(__file__).parent / "fixtures" / "test_fonts"


@pytest.fixture
def font_dir() -> Path:
    return FIXTURES


def test_scan_directory_finds_fonts(font_dir: Path) -> None:
    result = scan_directory(font_dir)
    assert isinstance(result, ScanResult)
    assert result.total_found >= 3
    assert len(result.fonts) >= 3
    assert result.scan_time_ms >= 0


def test_scanned_fonts_have_metadata(font_dir: Path) -> None:
    result = scan_directory(font_dir)
    for f in result.fonts:
        assert f.family
        assert f.style
        assert f.weight >= 0
        assert f.file_path.exists()


def test_scan_empty_directory(tmp_path: Path) -> None:
    result = scan_directory(tmp_path)
    assert result.total_found == 0
    assert len(result.fonts) == 0


def test_scan_ignores_non_fonts(tmp_path: Path) -> None:
    (tmp_path / "readme.txt").write_text("not a font")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    result = scan_directory(tmp_path)
    assert result.total_found == 0
