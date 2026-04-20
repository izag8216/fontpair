"""Font scanner -- discover locally installed fonts."""

from __future__ import annotations

import platform
import time
from pathlib import Path

from fontTools.ttLib import TTCollection, TTFont

from fontpair.models import FontInfo, ScanResult

_SYSTEM: str = platform.system()

_FONT_DIRS: dict[str, list[str]] = {
    "Darwin": [
        "~/Library/Fonts",
        "/Library/Fonts",
        "/System/Library/Fonts",
        "/System/Library/Fonts/Supplemental",
    ],
    "Linux": [
        "/usr/share/fonts",
        "~/.local/share/fonts",
        "~/.fonts",
        "/usr/local/share/fonts",
    ],
    "Windows": [
        "C:/Windows/Fonts",
        str(Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Fonts"),
    ],
}

_FONT_EXTENSIONS = {".ttf", ".otf", ".ttc"}


def get_font_directories() -> list[Path]:
    """Return platform-specific font directories."""
    dirs: list[Path] = []
    for raw in _FONT_DIRS.get(_SYSTEM, []):
        p = Path(raw).expanduser()
        if p.is_dir():
            dirs.append(p)
    return dirs


def _extract_font_info(tt: TTFont, file_path: Path) -> FontInfo:
    """Extract metadata from a TTFont object."""
    name_table = tt["name"]
    family = ""
    style = "Regular"

    for record in name_table.names:
        if record.nameID == 1:
            family = record.toUnicode()
        elif record.nameID == 2:
            style = record.toUnicode()

    if not family:
        family = file_path.stem

    weight = 400
    width = 5

    if "OS/2" in tt:
        os2 = tt["OS/2"]
        weight = os2.usWeightClass
        width = os2.usWidthClass

    return FontInfo(
        family=family,
        style=style,
        weight=weight,
        width=width,
        file_path=file_path,
    )


def _scan_file(file_path: Path) -> list[FontInfo]:
    """Scan a single font file, returning one FontInfo per face."""
    ext = file_path.suffix.lower()
    if ext not in _FONT_EXTENSIONS:
        return []

    try:
        if ext == ".ttc":
            ttc = TTCollection(file_path)
            results = []
            for i, tt in enumerate(ttc.fonts):
                info = _extract_font_info(tt, file_path)
                results.append(info)
            return results
        else:
            tt = TTFont(file_path)
            return [_extract_font_info(tt, file_path)]
    except Exception:
        return []


def scan_fonts(additional_dirs: list[Path] | None = None) -> ScanResult:
    """Scan all system font directories and return discovered fonts."""
    start = time.monotonic()
    fonts: list[FontInfo] = []
    seen_paths: set[Path] = set()

    dirs = get_font_directories()
    if additional_dirs:
        dirs.extend(additional_dirs)

    for font_dir in dirs:
        for file_path in font_dir.rglob("*"):
            if file_path.suffix.lower() not in _FONT_EXTENSIONS:
                continue
            resolved = file_path.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            fonts.extend(_scan_file(file_path))

    elapsed = (time.monotonic() - start) * 1000
    return ScanResult(fonts=fonts, total_found=len(fonts), scan_time_ms=elapsed)


def scan_directory(directory: Path) -> ScanResult:
    """Scan a specific directory for fonts (system dirs excluded)."""
    start = time.monotonic()
    fonts: list[FontInfo] = []
    seen_paths: set[Path] = set()

    for file_path in directory.rglob("*"):
        if file_path.suffix.lower() not in _FONT_EXTENSIONS:
            continue
        resolved = file_path.resolve()
        if resolved in seen_paths:
            continue
        seen_paths.add(resolved)
        fonts.extend(_scan_file(file_path))

    elapsed = (time.monotonic() - start) * 1000
    return ScanResult(fonts=fonts, total_found=len(fonts), scan_time_ms=elapsed)
