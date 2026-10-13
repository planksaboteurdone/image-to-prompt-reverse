"""Command-line entry point for image-to-prompt-reverse.

Usage:
    i2p reverse path/to/image.png --backend clip_interrogator --mode best
    i2p batch ./images --out ./prompts.jsonl --backend wd14_tagger
    i2p gui
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from i2p import __version__
from i2p.config.loader import load_config
from i2p.core.pipeline import ReversePipeline
from i2p.utils.logging import get_logger

log = get_logger(__name__)
console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="i2p")
def main() -> None:
    """image-to-prompt-reverse — turn images back into prompts."""


@main.command()
@click.argument("image", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--backend", default="clip_interrogator", show_default=True)
@click.option("--mode", type=click.Choice(["fast", "best", "classic"]), default="best")
@click.option("--config", "config_path", type=click.Path(path_type=Path), default=None)
def reverse(image: Path, backend: str, mode: str, config_path: Path | None) -> None:
    """Reverse a single image into a prompt."""
    cfg = load_config(config_path)
    pipe = ReversePipeline(cfg)
    result = pipe.run(image, backend=backend, mode=mode)
    console.print(f"[bold green]{result.prompt}[/]")
    if result.tags:
        console.print("[dim]tags:[/] " + ", ".join(result.tags))


@main.command()
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--out", type=click.Path(path_type=Path), default=Path("prompts.jsonl"))
@click.option("--backend", default="clip_interrogator", show_default=True)
def batch(folder: Path, out: Path, backend: str) -> None:
    """Reverse every image in a folder, streaming JSONL output."""
    cfg = load_config(None)
    pipe = ReversePipeline(cfg)
    images = sorted(p for p in folder.rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
    table = Table(title=f"Reversing {len(images)} images")
    table.add_column("file")
    table.add_column("prompt", overflow="fold")
    with out.open("w", encoding="utf-8") as fh:
        for img in images:
            try:
                res = pipe.run(img, backend=backend, mode="fast")
            except Exception as exc:  # noqa: BLE001 — batch must not die on one file
                log.warning("failed on %s: %s", img, exc)
                continue
            fh.write(json.dumps({"image": str(img), "prompt": res.prompt, "tags": res.tags}) + "\n")
            table.add_row(img.name, res.prompt[:80])
    console.print(table)


@main.command()
def gui() -> None:
    """Launch the PySide6 desktop app."""
    from i2p.gui.app import run_app

    sys.exit(run_app())


if __name__ == "__main__":
    main()