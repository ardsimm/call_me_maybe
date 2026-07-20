VENV ?= .venv

$(VENV):
	uv sync

install: $(VENV)

re: fclean install

run: install
	uv run python -m src

debug: install
	uv run python -m pdb src/__main__.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +

fclean: clean
	rm -rf .venv

flake8: install
	echo Running Flake8
	uv run python -m flake8 . --excelude=$(venv),llm_sdk

mypy: install
	echo Running Mypy
	uv run python -m mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude $(VENV);

lint: install
	echo Running Flake8;
	uv run python -m flake8 . --exclude=$(VENV),llm_sdk;
	echo Running Mypy;
	uv run python -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude $(VENV);

lint-strict: install
	echo Running Flake8;
	uv run python -m flake8 . --exclude=$(VENV),llm_sdk;
	echo Running Mypy;
	uv run python -m mypy . --strict --exclude $(VENV)

.phony: install run clean lint lint-strict flake8 mypy re
