# Repository Guidelines

## Project Structure & Module Organization
This repository is a small Python application scaffold.
- `main.py`: current entry point (`main()`), used for local execution.
- `pyproject.toml`: project metadata and Python version constraint (`>=3.14`).
- `README.md`: project overview (currently minimal; expand as features grow).
- `.venv/`: local virtual environment (not committed).

As the codebase grows, keep runtime code in top-level modules (or a package directory such as `ducksearch/`) and place tests under `tests/` with matching module names.

## Build, Test, and Development Commands
Use these commands from the repository root:
- `uv run python main.py`: run the current app entry point in the managed environment.
- `uv run pytest`: run tests (after adding `pytest` and `tests/`).
- `uv sync`: install/update dependencies from `pyproject.toml`.
- `uv pip install -e .`: install the project in editable mode when needed.

`uv` will manage the virtual environment automatically; manual activation is optional.

## Coding Style & Naming Conventions
Follow standard Python conventions (PEP 8):
- 4-space indentation, UTF-8 text, and trailing newline at end of files.
- `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Keep functions focused and small; prefer explicit names over abbreviations.

Recommended tooling as the project expands:
- `ruff` for linting and formatting.
- `pytest` for tests.

## Testing Guidelines
Add tests in `tests/` using filenames like `test_<module>.py`.
- Mirror source names where possible (example: `main.py` -> `tests/test_main.py`).
- Cover core behavior and edge cases for new logic.
- Run `uv run pytest` before opening a PR.

## Commit & Pull Request Guidelines
This repository has no commit history yet; adopt a clear, consistent standard now:
- Commit messages: imperative, concise subject (example: `Add CLI argument parsing`).
- Keep commits focused on one logical change.
- PRs should include: purpose, summary of changes, test evidence (`pytest` output), and linked issue(s) when applicable.
- For user-visible behavior changes, include example input/output in the PR description.
