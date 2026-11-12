"""Dataset CLI commands and Rich presentation."""

import csv
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from mew.data import load_csv, load_jsonl, validate_dataset

app = typer.Typer(help="Inspect and validate image-text datasets.", no_args_is_help=True)
console = Console()
error_console = Console(stderr=True)


@app.command()
def validate(
    path: Annotated[Path, typer.Argument(help="CSV or JSONL dataset to validate.")],
) -> None:
    """Validate a dataset and report all caption and image-path issues."""
    extension = path.suffix.lower()
    if extension not in {".csv", ".jsonl"}:
        error_console.print("Error: unsupported extension; expected .csv or .jsonl.", markup=False)
        raise typer.Exit(code=2)
    try:
        dataset = load_csv(path) if extension == ".csv" else load_jsonl(path)
    except (OSError, ValueError, csv.Error) as error:
        error_console.print(f"Error loading {path}: {error}", markup=False)
        raise typer.Exit(code=2) from None

    report = validate_dataset(dataset)
    console.print(
        f"Total: {report.total} | Valid: {report.valid} | Invalid: {report.invalid}",
        markup=False,
    )
    if report.issues:
        table = Table(title="Validation issues")
        table.add_column("Record", justify="right")
        table.add_column("Field", no_wrap=True)
        table.add_column("Code", no_wrap=True)
        table.add_column("Message", overflow="fold")
        for issue in report.issues:
            table.add_row(str(issue.record_index), issue.field, issue.code, Text(issue.message))
        console.print(table)
    else:
        console.print("Validation successful: no issues found.", markup=False)
    if not report.is_valid:
        raise typer.Exit(code=1)
