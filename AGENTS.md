# Working on MEW

MEW is a Python 3.11+ toolkit with a src layout. The distribution is
`mew-workbench`; the import package and CLI are `mew`.

## Git workflow

- `main` is stable. Never implement features directly on `main`.
- Before editing, check the current branch and working tree; preserve unrelated changes.
- Use `feat/<name>`, `fix/<name>`, or `refactor/<name>` branches. Create branches from
  an up-to-date `main` unless already on the correct feature branch.
- Use one feature branch per feature; multiple small commits are encouraged.
- Never automatically commit, push, open PRs, or merge without explicit instruction.
- Never force-push, use `reset --hard`, or discard user changes without permission.

## Task execution

- Read relevant code, tests, and requirements before editing.
- Implement only explicitly requested scope and interfaces. Prefer small,
  independently testable changes.
- Do not add unrelated refactoring, dependencies, or architectural changes.
- Ask before major architectural changes when specifications are incomplete.
- Use typed Python, focused modules, and standard library functionality where practical.

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

For every implementation change:

- Add or update focused pytest tests for behavioral changes.
- Run `uv run pytest` and `uv run ruff check .` after implementation.
- Fix failures caused by the change; report pre-existing failures separately.
- Inspect `git diff` before declaring the task complete.
- Never claim tests passed unless actually executed.

The full validation suite is:

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

## Review and delivery

- Report files changed, design decisions, test outcomes, and remaining concerns.
- Wait for explicit approval before committing or pushing. Use descriptive
  conventional commits, such as `feat(data): add dataset schema`.
- Integrate feature branches through GitHub PRs targeting `main`; require passing
  CI and human review before merging.
- Prefer squash merge for completed feature PRs while preserving small commits
  during development.
