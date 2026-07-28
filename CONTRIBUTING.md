# Contributing to SmartCore LLM Proxy

Thank you for helping make SmartCore safer and easier to use.

## Before you start

- Search existing issues before opening a new one.
- Use a bug report for reproducible failures and a feature request for proposed behavior.
- Never include API keys, `.env` contents, request payloads with private data, or unredacted logs.
- For vulnerabilities, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

## Development setup

SmartCore's validation tools support Python 3.10 or newer.

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
```

Activate the virtual environment, then run:

```bash
python -m unittest discover -s tests -v
python scripts/check_config.py config.yaml
```

To test the actual proxy, copy `.env.example` to `.env`, add test credentials with limited permissions, and install `requirements.txt`.

## Pull requests

1. Create a focused branch from `main`.
2. Keep credentials and generated runtime files out of commits.
3. Add or update tests for behavior changes.
4. Update both `README.md` and `README.ar.md` when user-facing setup changes.
5. Run all local checks.
6. Explain the motivation, behavior change, and validation in the pull request.

Small, focused pull requests are easier to review. By contributing, you agree that your contribution is licensed under the repository's MIT License.
