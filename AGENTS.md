# Working on MEW

MEW is a Python 3.11+ toolkit with a src layout. The distribution is
`mew-workbench`; the import package and CLI are `mew`.

## Git workflow

- `main` is stable. Never implement features directly on `main`.
- For every explicitly assigned implementation feature, manage Git and GitHub through
  PR delivery; the user should not need to run Git commands during normal development.
- Before editing, inspect `git status`, the current branch, remote configuration, and
  existing changes. Never discard unrelated work.
- For a new feature, fetch and update `main` using fast-forward only, then create a
  descriptively named `feat/<name>`, `fix/<name>`, or `refactor/<name>` branch.
  Reuse an existing feature branch when appropriate; use one branch per feature.
- Implement small, independently testable tasks. Before each commit, run relevant
  tests, `uv run pytest`, and `uv run ruff check .`, then review the diff.
- Stage only relevant files and create descriptive Conventional Commits, such as
  `feat(data): add dataset schema`. Commit incremental work as appropriate.
- When the complete feature is ready, push the feature branch and create a GitHub
  PR targeting `main` using `gh`.
- Never force-push, rewrite shared history, bypass checks, use `reset --hard`, or
  modify or discard unrelated changes without permission.
- If authentication, permissions, branch state, or CI blocks a step, report the
  blocker instead of taking unsafe shortcuts.

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
- Write an original, detailed PR title and description with Summary, Changes,
  Testing (actual commands and results), and Notes/Risks. Do not merely auto-fill
  from commit messages.
- Check GitHub Actions results, report failures, and provide the PR URL and final status.
- Never merge without explicit user approval. Require passing CI and human review;
  after approval, confirm required checks pass, squash merge, delete the feature
  branch, and synchronize local `main`.
