# Agent Instructions

- Use `uv` for Python dependency management and command execution.
- Use `pytest` for tests. Do not add `unittest`-style test classes unless explicitly requested.
- Run quality checks before completing code changes when tools are available:
  - `uv run pytest`
  - `uv run ruff check .`
  - `uv run ruff format --check .`
  - `uv run ty check`
  - `uv run prek run --all-files`
