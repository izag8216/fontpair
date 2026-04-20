"""Export pairings to CSS/JSON/YAML formats."""

from __future__ import annotations

import json
from io import StringIO

from fontpair.models import FontPair


def _css_fallback_stack(category: str) -> str:
    """Return a sensible fallback font stack."""
    stacks = {
        "serif": '"Georgia", "Times New Roman", serif',
        "sans-serif": '"Helvetica Neue", "Arial", sans-serif',
        "monospace": '"Courier New", "Courier", monospace',
        "display": '"Georgia", serif',
        "handwriting": '"Comic Sans MS", cursive',
    }
    return stacks.get(category, "sans-serif")


def _escape_family(family: str) -> str:
    """Quote font family name if it contains spaces."""
    if " " in family:
        return f'"{family}"'
    return family


def export_css(pairing: FontPair, include_local: bool = False) -> str:
    """Export pairing as CSS font-family declarations."""
    buf = StringIO()

    if include_local:
        if pairing.heading.file_path.exists():
            buf.write(f"@font-face {{\n")
            buf.write(f"  font-family: {_escape_family(pairing.heading.family)};\n")
            buf.write(f'  src: url("{pairing.heading.file_path}") format("truetype");\n')
            buf.write(f"  font-weight: {pairing.heading.weight};\n")
            buf.write("}\n\n")

        if pairing.body.file_path.exists():
            buf.write(f"@font-face {{\n")
            buf.write(f"  font-family: {_escape_family(pairing.body.family)};\n")
            buf.write(f'  src: url("{pairing.body.file_path}") format("truetype");\n')
            buf.write(f"  font-weight: {pairing.body.weight};\n")
            buf.write("}\n\n")

        if pairing.mono and pairing.mono.file_path.exists():
            buf.write(f"@font-face {{\n")
            buf.write(f"  font-family: {_escape_family(pairing.mono.family)};\n")
            buf.write(f'  src: url("{pairing.mono.file_path}") format("truetype");\n')
            buf.write(f"  font-weight: {pairing.mono.weight};\n")
            buf.write("}\n\n")

    heading_stack = _css_fallback_stack(pairing.heading.category.value)
    body_stack = _css_fallback_stack(pairing.body.category.value)

    buf.write(f":root {{\n")
    buf.write(f"  --font-heading: {_escape_family(pairing.heading.family)}, {heading_stack};\n")
    buf.write(f"  --font-body: {_escape_family(pairing.body.family)}, {body_stack};\n")
    if pairing.mono:
        mono_stack = _css_fallback_stack("monospace")
        buf.write(f"  --font-mono: {_escape_family(pairing.mono.family)}, {mono_stack};\n")
    buf.write("}\n")

    buf.write(f"\nh1, h2, h3, h4, h5, h6 {{\n")
    buf.write(f"  font-family: var(--font-heading);\n")
    buf.write(f"  font-weight: {pairing.heading.weight};\n")
    buf.write("}\n")

    buf.write(f"\nbody {{\n")
    buf.write(f"  font-family: var(--font-body);\n")
    buf.write(f"  font-weight: {pairing.body.weight};\n")
    buf.write("}\n")

    if pairing.mono:
        buf.write(f"\ncode, pre {{\n")
        buf.write(f"  font-family: var(--font-mono);\n")
        buf.write("}\n")

    return buf.getvalue()


def export_json(pairing: FontPair) -> str:
    """Export pairing as JSON."""
    return json.dumps(pairing.to_dict(), indent=2, ensure_ascii=False)


def export_yaml(pairing: FontPair) -> str:
    """Export pairing as YAML (no dependency required)."""
    data = pairing.to_dict()
    lines = []
    _dict_to_yaml(data, lines, indent=0)
    return "\n".join(lines)


def _dict_to_yaml(data: dict | list, lines: list[str], indent: int) -> None:
    prefix = "  " * indent
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, (dict, list)):
                lines.append(f"{prefix}{key}:")
                _dict_to_yaml(val, lines, indent + 1)
            elif val is None:
                lines.append(f"{prefix}{key}: null")
            elif isinstance(val, bool):
                lines.append(f"{prefix}{key}: {'true' if val else 'false'}")
            elif isinstance(val, (int, float)):
                lines.append(f"{prefix}{key}: {val}")
            else:
                lines.append(f'{prefix}{key}: "{val}"')
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(f"{prefix}-")
                _dict_to_yaml(item, lines, indent + 1)
            else:
                lines.append(f"{prefix}- {item}")


def export(pairing: FontPair, fmt: str = "css", include_local: bool = False) -> str:
    """Export pairing in the specified format."""
    if fmt == "css":
        return export_css(pairing, include_local=include_local)
    elif fmt == "json":
        return export_json(pairing)
    elif fmt == "yaml":
        return export_yaml(pairing)
    else:
        raise ValueError(f"Unsupported format: {fmt}. Use: css, json, yaml")
