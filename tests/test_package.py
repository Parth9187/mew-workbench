"""Smoke tests for package installation and module boundaries."""

import importlib
from importlib.metadata import version

import pytest

import mew


def test_version_matches_distribution() -> None:
    assert mew.__version__ == version("mew-workbench")


@pytest.mark.parametrize(
    "name",
    ["data", "models", "embeddings", "retrieval", "evaluation", "visualization", "reporting"],
)
def test_module_import(name: str) -> None:
    module = importlib.import_module(f"mew.{name}")
    assert module.__doc__
