VENV ?= .venv
NAME = call_me_maybe
TEST_NAME = run_tests

$(VENV): pyproject.toml
	uv sync

run: install
	uv run python -m src

install: $(VENV)

debug: install
	uv run python -m pdb src/__main__.py

test: install
	uv run python -m tests

build: install
	printf '#!/usr/bin/env bash\ncd "$$(dirname "$${BASH_SOURCE[0]}")"\nexec uv run python -m src "$$@"\n' > $(NAME)
	chmod +x $(NAME)

build-test: install
	printf '#!/usr/bin/env bash\ncd "$$(dirname "$${BASH_SOURCE[0]}")"\nexec uv run python -m tests "$$@"\n' > $(TEST_NAME)
	chmod +x $(TEST_NAME)

re:
	rm -f $(NAME)
	$(MAKE) build

re-test:
	rm -f $(TEST_NAME)
	$(MAKE) build-test

re-deps: fclean install

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name output -exec rm -rf {} +
	find . -type d -name stdout -exec rm -rf {} +
	find . -type d -name stderr -exec rm -rf {} +
	rm -f $(NAME) $(TEST_NAME)

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

.phony: install run debug test build build-test re re-test re-deps clean fclean flake8 mypy lint mypy-strict lint-strict black
