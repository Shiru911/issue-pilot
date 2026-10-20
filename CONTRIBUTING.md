# Contributing to IssuePilot

Thank you for your interest in contributing to IssuePilot! We welcome high-quality contributions from everyone.

---

## Code of Conduct

* Be respectful and constructive in all discussions.
* Focus on code quality, clarity, and comprehensive test coverage.
* Respect user privacy: never add telemetry, external tracking, or unprompted network calls.

---

## Development Workflow

1. Fork and clone the repository.
2. Create a virtual environment and install in editable mode:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   pip install -e ".[dev]"
   ```
3. Create a feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
4. Write clean, type-hinted code and add unit tests under `tests/`.
5. Run the test suite:
   ```bash
   pytest
   ```
6. Submit a Pull Request with a clear description of your changes.
