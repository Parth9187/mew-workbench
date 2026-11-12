# MEW — Multimodal Embedding Workbench

A Python toolkit for evaluating and exploring multimodal embeddings.
This repository currently provides the project foundation: package boundaries,
a command-line interface, tests, and CI. ML functionality is not implemented yet.

## Setup

Install Python 3.11+ and [uv](https://docs.astral.sh/uv/getting-started/installation/),
then run from the repository root:

```sh
uv sync --locked
uv run mew --help
uv run mew version
```

`uv sync` creates `.venv` and installs MEW in editable mode, including development
dependencies. `.python-version` selects Python 3.11 by default. To use another
supported interpreter, run `uv sync --locked --python 3.12`.

The equivalent module entry point is `uv run python -m mew`.

## Layout

```text
src/mew/
  cli.py          # Typer commands and Rich terminal output
  data/           # Dataset loading and schemas
  models/         # Model adapters
  embeddings/     # Generation, storage, transformations
  retrieval/      # Similarity search and ranking
  evaluation/     # Metrics and evaluation workflows
  visualization/  # Exploration and plotting
  reporting/      # Summaries and exports
tests/            # CLI and package smoke tests
examples/         # Usage examples
configs/          # Reserved for experiment configurations
```

Domain packages are placeholders with documented responsibilities. The only runtime
dependencies are Typer and Rich; no ML libraries are required.

## Development

```sh
uv sync --locked
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv build
```

Apply formatting with `uv run ruff format .`. Add dependencies with `uv add`, or
development tools with `uv add --dev`, and commit the updated `uv.lock`.
GitHub Actions runs tests, lint, formatting, CLI smoke checks, and package builds
on Python 3.11–3.14. See [AGENTS.md](AGENTS.md) for architecture and coding conventions.
