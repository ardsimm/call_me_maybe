VENV ?= .venv

$(VENV):
	uv sync

install: $(VENV)

run: install
	uv run python -m src

debug: install
	uv run python -m pdb src

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache

fclean: clean
	rm -rf .venv

lint:
	echo Running Flake8
	flake8 . --exclude=$(VENV),llm_sdk
	echo Running Mypy
	mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude $(VENV)

lint-strict:
	echo Running Flake8
	flake8 . --exclude=$(VENV),llm_sdk
	echo Running Mypy
	mypy src --strict --exclude $(VENV) --exclude llm_sdk

.phony: install run clean lint lint-strict
