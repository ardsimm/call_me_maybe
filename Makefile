VENV ?= .venv

$(VENV): pyproject.toml
	uv sync

install: $(VENV)

re: fclean install

run: install
	uv run python -m src

debug: install
	uv run python -m pdb src/__main__.py

test: install
	uv run python -m tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +

fclean: clean
	rm -rf .venv

flake8: install
	echo Running Flake8
	uv run python -m flake8 . --exclude=$(VENV),llm_sdk

mypy: install
	echo Running Mypy
	uv run python -m mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude $(VENV);

lint: install flake8 mypy

mypy-strict: install
	echo Running Mypy
	uv run python -m mypy . --strict --exclude $(VENV)

lint-strict: flake8 mypy-strict

black: install
	uv run python -m black --line-length 79 .

.phony: install re run debug test clean fclean flake8 mypy lint mypy-strict lint-strict black
