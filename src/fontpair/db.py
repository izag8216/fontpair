"""SQLite cache for font metadata."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from fontpair.models import FontCategory, FontInfo, FontMetrics

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS fonts (
    family TEXT NOT NULL,
    style TEXT NOT NULL,
    weight INTEGER NOT NULL,
    width INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'sans-serif',
    metrics_json TEXT,
    scanned_at REAL NOT NULL,
    PRIMARY KEY (family, style, file_path)
)
"""


def _db_path() -> Path:
    return Path.home() / ".cache" / "fontpair" / "fonts.db"


def get_connection() -> sqlite3.Connection:
    db_file = _db_path()
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    conn.execute(_CREATE_TABLE)
    conn.commit()
    return conn


def save_fonts(conn: sqlite3.Connection, fonts: list[FontInfo]) -> None:
    """Save font info to cache."""
    import time

    now = time.time()
    for f in fonts:
        metrics_json = json.dumps(f.metrics.to_dict()) if f.metrics else None
        conn.execute(
            """INSERT OR REPLACE INTO fonts
               (family, style, weight, width, file_path, category, metrics_json, scanned_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f.family,
                f.style,
                f.weight,
                f.width,
                str(f.file_path),
                f.category.value,
                metrics_json,
                now,
            ),
        )
    conn.commit()


def load_fonts(conn: sqlite3.Connection) -> list[FontInfo]:
    """Load all cached fonts."""
    rows = conn.execute("SELECT * FROM fonts ORDER BY family, style").fetchall()
    fonts = []
    for row in rows:
        metrics = None
        if row["metrics_json"]:
            md = json.loads(row["metrics_json"])
            metrics = FontMetrics(**md)
        fonts.append(
            FontInfo(
                family=row["family"],
                style=row["style"],
                weight=row["weight"],
                width=row["width"],
                file_path=Path(row["file_path"]),
                category=FontCategory(row["category"]),
                metrics=metrics,
            )
        )
    return fonts
