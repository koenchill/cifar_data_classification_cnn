.PHONY: install install-cpu lint test precommit phase lock

# Prefer repo venv if present.
PYTHON ?= $(if $(wildcard .venv/Scripts/python.exe),.venv/Scripts/python.exe,$(if $(wildcard .venv/bin/python),.venv/bin/python,python))

install:
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e ".[dev]"

# Prefer for Linux CI / CPU-only reproducibility.
install-cpu:
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -e ".[dev]" --extra-index-url https://download.pytorch.org/whl/cpu

lock:
	$(PYTHON) -m pip freeze > requirements.lock

lint:
	$(PYTHON) -m ruff check src tests scripts
	$(PYTHON) -m mypy
	$(PYTHON) -m bandit -c pyproject.toml -r src

test:
	pytest -q

precommit:
	pre-commit run --all-files

phase:
	@echo "Open docs/implementation/CURSOR_EXECUTION_PLAN.md and run one phase card."
