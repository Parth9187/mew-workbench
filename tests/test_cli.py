"""Tests for the public CLI contract."""

from typer.testing import CliRunner

from mew import __version__
from mew.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Multimodal Embedding Workbench" in result.output
    assert "version" in result.output


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == f"MEW {__version__}"


def test_unknown_command() -> None:
    result = runner.invoke(app, ["unknown"])
    assert result.exit_code == 2
