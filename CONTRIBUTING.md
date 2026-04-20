# Contributing to fontpair

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/izag8216/fontpair.git
cd fontpair
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

We use [ruff](https://docs.astral.sh/ruff/) for linting:

```bash
ruff check src/ tests/
```

## Commit Convention

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `refactor:` code restructuring
- `test:` test additions/changes
- `chore:` build, CI, tooling

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`feat/my-feature`)
3. Add tests for any new functionality
4. Ensure all tests pass (`pytest`)
5. Ensure linting passes (`ruff check`)
6. Submit a pull request

## Reporting Issues

- Use GitHub Issues
- Include OS, Python version, and fontpair version
- Provide steps to reproduce
