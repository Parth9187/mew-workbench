"""Command-line entry point for MEW."""

import typer
from rich.console import Console

from mew import __version__

app = typer.Typer(
    name="mew",
    help="MEW: Multimodal Embedding Workbench.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.callback()
def main() -> None:
    """Evaluate and explore multimodal embeddings."""


@app.command()
def version() -> None:
    """Show the installed MEW version."""
    console.print(f"MEW {__version__}", markup=False)
