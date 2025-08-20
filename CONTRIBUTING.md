## Contributing to Lambda Layer Generator

Thank you for your interest in contributing! This project welcomes issues, discussions, documentation, and code.

By participating, you agree to follow the project’s `CODE_OF_CONDUCT.md`.

### Ways to contribute
- **Bug reports**: Include steps to reproduce, expected vs actual behavior, logs, and environment details.
- **Feature proposals**: Explain the use case, proposed API/UX, and alternatives considered.
- **Documentation**: Improve `README.md`, inline docs, and usage examples.
- **Code**: Fix bugs, add features, improve performance, or refactor for clarity.

## Development quickstart
```bash
# 1) Create a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Configure AWS credentials (if running end-to-end)
cp env.example .env
# Edit .env to include AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_DEFAULT_REGION

# 4) Run the CLI
python main.py "requests,pydantic==2.5.0"
```

### Project overview
- `main.py`: CLI entrypoint
- `src/layer_generator.py`: Orchestrates the end-to-end layer build and publish flow
- `src/layer_builder.py`: Builds the layer content and zip package
- `src/aws_client.py`: Boto3 Lambda client wrapper; all AWS calls go through here
- `src/package_parser.py`: Parses and validates package spec strings
- `src/logger.py`: Pretty logging and verbosity control

## Coding standards
- **Compatibility**: Keep runtime-compatible with Python 3.8–3.12.
- **Types**: Use type hints on public functions and complex internals.
- **Errors**: Prefer explicit exceptions with actionable messages. Fail fast; avoid silent failures.
- **Logging**: Use `src/logger.py` (not `print`). Respect quiet/JSON modes; do not emit noisy logs in library code.
- **Structure**: Small, focused functions; early returns over deep nesting.
- **AWS interactions**: Go through `src/aws_client.py` for easier mocking and centralized retries/backoff.
- **I/O and subprocess**: Validate inputs; handle timeouts; sanitize/normalize paths; clean up temp files.
- **CLI**: Keep output stable in `--json` mode; update `--help` text when adding flags.
- **Docs**: Update `README.md` and docstrings for any user-facing changes.

## Testing
- Use `pytest` (place tests under `tests/`). Mock AWS with `moto` or stub `src/aws_client.py`.
- Cover error paths and edge cases (missing creds, bad packages, network failures, etc.).
- Prefer unit tests; add optional e2e tests guarded by env flags if they require real AWS.
- Suggested commands:
```bash
pytest -q
```

## Commit and PR process
- **Issues first**: For non-trivial changes, open an issue to discuss the approach.
- **Branching**: `feature/<short-name>` or `fix/<short-name>`.
- **Commit style**: Conventional Commits (e.g., `feat: add python3.12 runtime`, `fix: handle invalid specifiers`).
- **PR checklist**:
  - Tests added/updated and passing
  - Docs updated (`README.md`, usage, flags)
  - No regressions in `--json` output
  - No direct `boto3` calls outside `src/aws_client.py`
  - Meaningful error messages and robust handling

### How to submit a PR
1. Fork the repo and create a topic branch
2. Make changes with tests and docs
3. Run tests locally and ensure the CLI works
4. Open a PR describing the change, rationale, and impact

## Reporting security issues
Please do not open public issues for security vulnerabilities. Email the maintainers at `tareq.iiuc.eb@gmail.com` (replace with the project’s real contact) with details and reproduction steps.

## License
By contributing, you agree that your contributions are licensed under the project’s MIT License. 