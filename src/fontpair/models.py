"""Data models for fontpair."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class FontCategory(Enum):
    SERIF = "serif"
    SANS_SERIF = "sans-serif"
    MONOSPACE = "monospace"
    DISPLAY = "display"
    HANDWRITING = "handwriting"


@dataclass(frozen=True)
class FontMetrics:
    x_height_ratio: float
    weight: int
    avg_width: float
    contrast: float

    def to_dict(self) -> dict:
        return {
            "x_height_ratio": round(self.x_height_ratio, 4),
            "weight": self.weight,
            "avg_width": round(self.avg_width, 2),
            "contrast": round(self.contrast, 4),
        }


@dataclass(frozen=True)
class FontInfo:
    family: str
    style: str
    weight: int
    width: int
    file_path: Path
    category: FontCategory = FontCategory.SANS_SERIF
    metrics: FontMetrics | None = None

    def to_dict(self) -> dict:
        return {
            "family": self.family,
            "style": self.style,
            "weight": self.weight,
            "width": self.width,
            "file_path": str(self.file_path),
            "category": self.category.value,
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }


@dataclass(frozen=True)
class ScoreBreakdown:
    visual_harmony: float
    readability: float
    contrast_balance: float
    x_height_compat: float
    total: float

    def to_dict(self) -> dict:
        return {
            "visual_harmony": round(self.visual_harmony, 1),
            "readability": round(self.readability, 1),
            "contrast_balance": round(self.contrast_balance, 1),
            "x_height_compat": round(self.x_height_compat, 1),
            "total": round(self.total, 1),
        }


@dataclass(frozen=True)
class FontPair:
    heading: FontInfo
    body: FontInfo
    mono: FontInfo | None = None
    score: ScoreBreakdown | None = None
    style_description: str = ""

    def to_dict(self) -> dict:
        result = {
            "heading": self.heading.to_dict(),
            "body": self.body.to_dict(),
            "score": self.score.to_dict() if self.score else None,
            "style_description": self.style_description,
        }
        if self.mono:
            result["mono"] = self.mono.to_dict()
        return result


@dataclass
class ScanResult:
    fonts: list[FontInfo] = field(default_factory=list)
    total_found: int = 0
    scan_time_ms: float = 0.0


@dataclass(frozen=True)
class RecommendOptions:
    style: str = "modern"
    count: int = 5
    filter_families: list[str] = field(default_factory=list)
    include_mono: bool = True
