VENV ?= .venv
NAME = call_me_maybe
TEST_NAME = run_tests

$(VENV): pyproject.toml
	uv sync

run: install
	uv run python -m src

showcase: install
	uv run python -m src --input data/input/function_calling_showcase.json

install: $(VENV)

debug: install
	uv run python -m pdb -m src

test: install
	uv run python -m tests

re: fclean install

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
	uv run python -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude $(VENV) --exclude tests

lint: install flake8 mypy

mypy-strict: install
	echo Running Mypy
	uv run python -m mypy . --strict --exclude $(VENV) --exclude tests

lint-strict: flake8 mypy-strict

black: install
	uv run python -m black --line-length 79 .

.PHONY: install run debug test re re-test re-deps clean fclean flake8 mypy lint mypy-strict lint-strict black showcase
