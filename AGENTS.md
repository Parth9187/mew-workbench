# Working on MEW

MEW is a Python 3.11+ toolkit with a src layout. The distribution is
`mew-workbench`; the import package and CLI are `mew`.

## Architecture

- `src/mew/cli.py`: Typer commands and Rich terminal output; keep commands thin.
- `src/mew/data/`: dataset loading, validation, and modality schemas.
- `src/mew/models/`: model adapter interfaces and optional integrations.
- `src/mew/embeddings/`: embedding generation, storage, and transformations.
- `src/mew/retrieval/`: similarity search and ranking.
- `src/mew/evaluation/`: metrics and evaluation orchestration.
- `src/mew/visualization/`: exploration and plotting.
- `src/mew/reporting/`: summaries and report export.
- `tests/`: pytest tests for public behavior.
- `examples/` and `configs/`: usage examples and future experiment configuration.

The domain packages are intentionally empty boundaries. Do not add ML functionality,
speculative abstractions, or heavyweight dependencies as part of foundation work.
As features arrive, put domain logic in its owning package and avoid cyclic imports.
Keep optional model and plotting integrations out of core package imports.

## Conventions

Use small, focused modules, type annotations on functions, and docstrings for public
interfaces. Use pathlib for filesystem paths. Avoid import-time side effects.
Keep CLI presentation separate from domain logic. Add dependencies only when a
concrete feature needs them. The version in `pyproject.toml` is the source of truth;
`mew.__version__` reads installed distribution metadata.

Use uv for dependency management and commit `uv.lock` when dependencies change.
Use Ruff formatting and linting (100-column lines, Python 3.11 target).
Test observable behavior and error cases with pytest; use Typer's CliRunner for commands.

## Validation

```sh
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run mew --help
uv run mew version
uv build
```

CI runs these checks on Python 3.11 through 3.14. Update documentation and tests
alongside changes to public behavior.
