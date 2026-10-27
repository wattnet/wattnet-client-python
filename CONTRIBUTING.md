# Contributing to wattnet-client

Thank you for your interest in contributing. This document covers how to set up your environment, the code standards we follow, and the process for submitting changes.

## Prerequisites

- Python ≥ 3.10
- [Poetry](https://python-poetry.org/) ≥ 2.0
- Git

## Getting Started

1. Fork the repository and clone your fork:

   ```bash
   git clone https://github.com/<your-username>/wattnet-client-python.git
   cd wattnet-client-python
   ```

2. Install all dependency groups:

   ```bash
   poetry install --with dev,test,lint,types,security
   ```

3. Install the pre-commit hooks:

   ```bash
   pre-commit install --hook-type pre-commit --hook-type commit-msg
   ```

## Running the Tests

**Unit tests** (HTTP is mocked, no external services needed):

```bash
poetry run pytest tests/unit/
```

**Integration tests** (hit a real, running `wattnet-api` instance, skipped automatically unless `WATTNET_TEST_BASE_URL` and `WATTNET_TEST_TOKEN` are set):

```bash
export WATTNET_TEST_BASE_URL=http://localhost:8000/v1
export WATTNET_TEST_TOKEN=<a valid bearer token>
poetry run pytest tests/integration/
```

Or via tox:

```bash
tox -e integration
```

**Full tox matrix** (unit tests on py3.10–3.15, lint, type-check, format, security, dependency audit, build):

```bash
tox
```

## Code Style

We enforce a consistent style automatically. Before opening a PR, run:

```bash
# Format and lint
ruff format wattnet/
ruff check wattnet/

# Type-check
mypy -p wattnet.client

# Security scan
bandit -r wattnet/
```

All of these also run via pre-commit on every commit and are verified in CI.

Key rules:
- Line length: 88 characters (Ruff default).
- Import order: standard library → third-party → first-party, enforced by Ruff's isort rules.
- Docstrings: required on all public modules, classes, and functions, enforced by Ruff's pydocstyle rules with the pep257 convention.
- Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`).

## Adding a new endpoint

`wattnet-client` maps each wattnet-api endpoint 1:1 to a client method. To add one:

1. Add a `@decorators.get("/path")`-decorated stub method to `WattnetRawClient` (`wattnet/client/raw_client.py`), matching the API router's query parameters exactly.
2. Add the matching override to `WattnetClient` (`wattnet/client/client.py`), decorated with `@dataframe(block=...)` describing how to flatten its JSON shape (see the docstring on `wattnet.client.decorators.dataframe` and the table in the module docstring of `wattnet/client/flatten.py`).
3. Add unit tests mocking the new endpoint in `tests/unit/test_client.py`.

## Submitting a Pull Request

1. Create a branch from `main` with a descriptive name:

   ```bash
   git checkout -b feat/my-new-feature
   ```

2. Make your changes, ensuring all tests pass and the linter is clean.

3. Push your branch and open a PR against `main`. Fill in the PR template.

4. A maintainer will review your PR. Please address any requested changes promptly.

## Reporting Issues

Please use the GitHub issue templates for bug reports and feature requests. For security vulnerabilities, see [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
