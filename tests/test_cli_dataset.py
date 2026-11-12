"""Tests for the dataset validation CLI contract."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mew import __version__
from mew.cli import app

runner = CliRunner()


@pytest.mark.parametrize("extension", [".csv", ".CSV", ".jsonl", ".JSONL"])
def test_valid_dataset(tmp_path: Path, extension: str) -> None:
    (tmp_path / "cat.jpg").touch()
    path = tmp_path / f"dataset{extension}"
    content = (
        "image_path,caption\ncat.jpg,Cat\n"
        if extension.lower() == ".csv"
        else json.dumps({"image_path": "cat.jpg", "caption": "Cat"})
    )
    path.write_text(content, encoding="utf-8")

    result = runner.invoke(app, ["dataset", "validate", str(path)])

    assert result.exit_code == 0
    assert "Total: 1 | Valid: 1 | Invalid: 0" in result.output
    assert "Validation successful: no issues found." in result.output
    assert "Validation issues" not in result.output


@pytest.mark.parametrize("extension", ["csv", "jsonl"])
def test_invalid_dataset_and_all_issues(tmp_path: Path, extension: str) -> None:
    (tmp_path / "cat.jpg").touch()
    path = tmp_path / f"dataset.{extension}"
    content = (
        "image_path,caption\ncat.jpg,Cat\nmissing.gif,\nmissing.png,Missing\n"
        if extension == "csv"
        else "\n".join(
            json.dumps(record)
            for record in [
                {"image_path": "cat.jpg", "caption": "Cat"},
                {"image_path": "missing.gif", "caption": ""},
                {"image_path": "missing.png", "caption": "Missing"},
            ]
        )
    )
    path.write_text(content, encoding="utf-8")

    result = runner.invoke(app, ["dataset", "validate", str(path)], terminal_width=180)

    assert result.exit_code == 1
    assert "Total: 3 | Valid: 1 | Invalid: 2" in result.output
    for text in ["Record", "Field", "Code", "Message", "empty_caption", "unsupported_extension"]:
        assert text in result.output
    assert result.output.count("missing_image") == 2
    assert "Caption must not be blank." in result.output
    assert "Validation successful" not in result.output


@pytest.mark.parametrize("extension", ["csv", "jsonl"])
def test_empty_dataset(tmp_path: Path, extension: str) -> None:
    path = tmp_path / f"empty.{extension}"
    path.write_text("image_path,caption\n" if extension == "csv" else "", encoding="utf-8")

    result = runner.invoke(app, ["dataset", "validate", str(path)])

    assert result.exit_code == 0
    assert "Total: 0 | Valid: 0 | Invalid: 0" in result.output
    assert "Validation successful" in result.output


@pytest.mark.parametrize("name", ["dataset.txt", "dataset", "dataset.json"])
def test_unsupported_extension(tmp_path: Path, name: str) -> None:
    result = runner.invoke(app, ["dataset", "validate", str(tmp_path / name)])

    assert result.exit_code == 2
    assert "unsupported extension" in result.output
    assert "Traceback" not in result.output


@pytest.mark.parametrize("extension", ["csv", "jsonl"])
def test_missing_file(tmp_path: Path, extension: str) -> None:
    result = runner.invoke(app, ["dataset", "validate", str(tmp_path / f"missing.{extension}")])

    assert result.exit_code == 2
    assert "Error loading" in result.output
    assert "No such file" in " ".join(result.output.split())
    assert "Traceback" not in result.output


@pytest.mark.parametrize(
    ("extension", "content", "message"),
    [
        ("csv", "caption\nCat\n", "missing required headers"),
        ("csv", "image_path,caption\ncat.jpg\n", "incomplete row"),
        ("jsonl", "{", "malformed JSON"),
        ("jsonl", "[]", "expected a JSON object"),
    ],
)
def test_malformed_file(tmp_path: Path, extension: str, content: str, message: str) -> None:
    path = tmp_path / f"malformed.{extension}"
    path.write_text(content, encoding="utf-8")

    result = runner.invoke(app, ["dataset", "validate", str(path)])

    assert result.exit_code == 2
    assert message in " ".join(result.output.split())
    assert "Traceback" not in result.output


def test_invalid_encoding(tmp_path: Path) -> None:
    path = tmp_path / "invalid.jsonl"
    path.write_bytes(b"\xff")

    result = runner.invoke(app, ["dataset", "validate", str(path)])

    assert result.exit_code == 2
    assert "Error loading" in result.output
    assert "Traceback" not in result.output


@pytest.mark.parametrize(
    "arguments", [["--help"], ["dataset", "--help"], ["dataset", "validate", "--help"]]
)
def test_help(arguments: list[str]) -> None:
    result = runner.invoke(app, arguments)

    assert result.exit_code == 0
    assert "dataset" in result.output.lower()


def test_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.output.strip() == f"MEW {__version__}"
