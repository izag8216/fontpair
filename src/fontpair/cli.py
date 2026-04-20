"""CLI entry point for fontpair."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fontpair import __version__
from fontpair.analyzer import analyze_font_info, compute_metrics
from fontpair.categorizer import categorize, categorize_fonts
from fontpair.db import get_connection, load_fonts, save_fonts
from fontpair.exporter import export
from fontpair.models import FontCategory, RecommendOptions
from fontpair.recommender import recommend
from fontpair.scanner import scan_directory, scan_fonts

console = Console()


def _category_style(cat: FontCategory) -> str:
    styles = {
        FontCategory.SERIF: "[bold red]serif[/]",
        FontCategory.SANS_SERIF: "[bold blue]sans-serif[/]",
        FontCategory.MONOSPACE: "[bold green]monospace[/]",
        FontCategory.DISPLAY: "[bold magenta]display[/]",
        FontCategory.HANDWRITING: "[bold yellow]handwriting[/]",
    }
    return styles.get(cat, str(cat))


@click.group()
@click.version_option(__version__, prog_name="fontpair")
def cli() -> None:
    """fontpair -- Local Font Pairing Recommender."""
    pass


@cli.command()
@click.option("--refresh", is_flag=True, help="Force re-scan (ignore cache)")
@click.option("--dir", "directory", type=click.Path(), help="Scan specific directory")
def scan(refresh: bool, directory: str | None) -> None:
    """Scan locally installed fonts."""
    with console.status("[bold green]Scanning fonts..."):
        if directory:
            result = scan_directory(Path(directory))
        else:
            result = scan_fonts()

    fonts = categorize_fonts(result.fonts)

    conn = get_connection()
    save_fonts(conn, fonts)
    conn.close()

    table = Table(title=f"Found {result.total_found} fonts ({result.scan_time_ms:.0f}ms)")
    table.add_column("#", style="dim", width=4)
    table.add_column("Family", style="bold")
    table.add_column("Style")
    table.add_column("Weight", justify="right")
    table.add_column("Category")
    table.add_column("Path", style="dim", max_width=40, overflow="ellipsis")

    for i, f in enumerate(fonts, 1):
        table.add_row(
            str(i),
            f.family,
            f.style,
            str(f.weight),
            _category_style(f.category),
            str(f.file_path),
        )

    console.print(table)


@cli.command()
@click.argument("family")
def info(family: str) -> None:
    """Show detailed info for a font family."""
    conn = get_connection()
    fonts = load_fonts(conn)
    conn.close()

    matches = [f for f in fonts if family.lower() in f.family.lower()]

    if not matches:
        console.print(f"[red]No fonts matching '{family}' found.[/]")
        console.print("Run [bold]fontpair scan[/] first.")
        sys.exit(1)

    for f in matches[:5]:
        detail = analyze_font_info(f.file_path) if f.file_path.exists() else {}

        content_lines = [
            f"[bold]Family:[/] {f.family}",
            f"[bold]Style:[/] {f.style}",
            f"[bold]Weight:[/] {f.weight}",
            f"[bold]Width class:[/] {f.width}",
            f"[bold]Category:[/] {_category_style(f.category)}",
            f"[bold]Path:[/] {f.file_path}",
        ]

        if detail:
            content_lines.extend([
                f"[bold]Glyphs:[/] {detail.get('glyph_count', '?')}",
                f"[bold]UPM:[/] {detail.get('units_per_em', '?')}",
                f"[bold]X-height:[/] {detail.get('x_height', '?')}",
                f"[bold]Ascender:[/] {detail.get('ascender', '?')}",
                f"[bold]Cap height:[/] {detail.get('cap_height', '?')}",
            ])

        if f.metrics:
            content_lines.extend([
                f"[bold]X-height ratio:[/] {f.metrics.x_height_ratio:.4f}",
                f"[bold]Avg width:[/] {f.metrics.avg_width:.2f}",
                f"[bold]Contrast:[/] {f.metrics.contrast:.4f}",
            ])

        console.print(Panel(
            "\n".join(content_lines),
            title=f.family,
            border_style="blue",
        ))


@cli.command()
@click.option("--style", type=click.Choice(["modern", "classic", "playful", "editorial", "technical", "minimal"]), default="modern")
@click.option("--count", "-n", default=5, help="Number of pairings to show")
@click.option("--filter", "filter_families", multiple=True, help="Restrict to these font families")
@click.option("--no-mono", is_flag=True, help="Skip monospace recommendations")
def recommend_cmd(
    style: str,
    count: int,
    filter_families: tuple[str, ...],
    no_mono: bool,
) -> None:
    """Recommend font pairings."""
    conn = get_connection()
    fonts = load_fonts(conn)
    conn.close()

    if not fonts:
        console.print("[red]No fonts in cache.[/] Run [bold]fontpair scan[/] first.")
        sys.exit(1)

    opts = RecommendOptions(
        style=style,
        count=count,
        filter_families=list(filter_families),
        include_mono=not no_mono,
    )

    with console.status(f"[bold green]Finding {style} pairings..."):
        pairs = recommend(fonts, opts)

    if not pairs:
        console.print("[yellow]No suitable pairings found. Try a different style or add more fonts.[/]")
        sys.exit(0)

    for i, pair in enumerate(pairs, 1):
        score = pair.score
        score_str = f"{score.total:.1f}" if score else "N/A"

        heading_line = f"[bold]{pair.heading.family}[/] ({pair.heading.style}, w{pair.heading.weight})"
        body_line = f"[bold]{pair.body.family}[/] ({pair.body.style}, w{pair.body.weight})"
        mono_line = ""
        if pair.mono:
            mono_line = f"\n  Code: [bold]{pair.mono.family}[/] ({pair.mono.style})"

        content = f"  Heading: {heading_line}\n  Body: {body_line}{mono_line}"

        if score:
            content += (
                f"\n\n  [dim]Harmony: {score.visual_harmony:.0f} | "
                f"Readability: {score.readability:.0f} | "
                f"Contrast: {score.contrast_balance:.0f} | "
                f"X-height: {score.x_height_compat:.0f}[/]"
            )

        if pair.style_description:
            content += f"\n  [dim italic]{pair.style_description}[/]"

        console.print(Panel(
            content,
            title=f"#{i}  Score: {score_str}",
            border_style="green" if (score and score.total >= 75) else "yellow",
        ))


@cli.command("export")
@click.option("--pairing", "-p", type=int, required=True, help="Pairing number from recommend output")
@click.option("--format", "fmt", type=click.Choice(["css", "json", "yaml"]), default="css")
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
@click.option("--local", "include_local", is_flag=True, help="Include @font-face declarations")
@click.option("--style", type=click.Choice(["modern", "classic", "playful", "editorial", "technical", "minimal"]), default="modern")
def export_cmd(pairing: int, fmt: str, output: str | None, include_local: bool, style: str) -> None:
    """Export a pairing as CSS/JSON/YAML."""
    conn = get_connection()
    fonts = load_fonts(conn)
    conn.close()

    if not fonts:
        console.print("[red]No fonts in cache.[/] Run [bold]fontpair scan[/] first.")
        sys.exit(1)

    opts = RecommendOptions(style=style, count=pairing)
    pairs = recommend(fonts, opts)

    if not pairs or pairing > len(pairs):
        console.print(f"[red]Pairing #{pairing} not found.[/] Run recommend first.")
        sys.exit(1)

    selected = pairs[pairing - 1]
    result = export(selected, fmt=fmt, include_local=include_local)

    if output:
        Path(output).write_text(result)
        console.print(f"[green]Exported to {output}[/]")
    else:
        console.print(result)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
