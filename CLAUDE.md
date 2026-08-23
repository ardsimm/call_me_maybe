# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A function-calling tool that turns a natural-language prompt (e.g. "What is the sum of 2 and 3?") into a
structured function call (`{"name": "fn_add_numbers", "parameters": {"a": 2.0, "b": 3.0}}`), driven by a small
local LLM (`Qwen/Qwen3-0.6B` by default, via `llm_sdk.Small_LLM_Model`). Small models are unreliable at freeform
JSON generation, so this project does **not** prompt-and-hope: it implements **constrained decoding**, masking
the model's logits at every generation step so only tokens that keep the output structurally/schema-valid can
ever be picked. See `private/en.subject.pdf` for the full assignment spec (school project, 42-style).

## Commands

```sh
make install       # uv sync
make run           # uv run python -m src   (reads data/input/, writes data/output/)
make debug         # uv run python -m pdb src/__main__.py
make lint          # flake8 . (excludes .venv, llm_sdk) + mypy src --warn-return-any --warn-unused-ignores
                    #   --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
make lint-strict    # flake8 . + mypy . --strict
make black          # uv run python -m black --line-length 79 .
make clean / fclean # remove __pycache__/.mypy_cache, or also the venv
```

Run directly with custom paths (defaults are `data/input/functions_definition.json`, `data/input/function_calling_tests.json`, `data/output/<output>`):

```sh
uv run python -m src --functions_definition <file> --input <file> --output <file> --model <hf-model-id>
```

There is no test suite in this repo (the subject explicitly says tests are for your own verification and are not
submitted/graded).

## Architecture

Everything under `src/` is organized as small ABC-based modules, each with a `*_factory.py` returning a
singleton/instance and a private `__*_impl.py` holding the concrete implementation — follow this pattern when
adding new variants (e.g. a new `State`, `Adapter`, `Tokenizer`). Modules with double-underscore filenames
(`__generator_impl.py`, `__json_adapter.py`, ...) are intentionally not part of the package's public API.

Entry point: `src/__main__.py` → `CallMeMaybe.run()` (`src/call_me_maybe.py`), which:
1. Parses CLI args into `Arguments` (pydantic model, validated against the input JSON files at construction).
2. Builds a `Context` (`src/models/context.py`) — loads and validates `functions_definition.json` into
   `Function`/`Parameter` models, and the prompts file into a list of strings. Both files are strictly validated
   (missing/extra keys, wrong types → `ParsingError`).
3. For each prompt, calls the `Generator` twice: `generate_name()` then `generate_parameters()`.
4. Writes all `OutputItem`s (`{prompt, name, parameters}`) as one JSON array via `AdapterFactory` (JSON adapter).

### The constrained-decoding pipeline

This is the core of the project, spread across four cooperating layers:

- **`Model`** (`src/model/model.py`) — singleton wrapper around `llm_sdk.Small_LLM_Model`. Adds
  `string_end_sequences`: every vocab token whose surface text contains an unescaped `"`, computed once from the
  SDK's vocab file. This is the primitive used everywhere to know which tokens legally close a JSON string.
- **`State`** (`src/state/state.py`) — a finite-state-machine base class: a list of `_stages`, and per-stage maps
  of `allowed_tokens` (what may be emitted now) and `transition_tokens` (which emitted tokens advance to the next
  stage). `get_allowed_tokens() -> None` (as opposed to `[]`, meaning "no constraint from this state") signals
  end-of-generation. Concrete states: `IntState`, `FloatState`, `StringState` (each type-specific, all end on a
  `string_end_sequences` token) and `TrieState` (`src/state/trie_state.py`, backed by `src/trie/trie.py`) — walks
  a token-level trie built from a fixed set of allowed words (e.g. valid function names, or `"true"`/`"false"`),
  raising `GenerationError` if a forbidden token is ever picked. Build new states via `StateFactory`
  (`src/state/state_factory.py`).
- **`Constrainer`** (`src/constrainer/__constrainer_impl.py`) — given raw logits and a `State`, picks
  `argmax(logits)` restricted to `state.get_allowed_tokens()`, then calls `state.update_last_token()` to drive the
  state machine forward. Returns `None` once the state signals completion.
- **`Generator`** (`src/generate/__generator_impl.py`) — orchestrates prompt building (`src/prompting/`) +
  token-by-token decode loop (`__get_completion`) using a `Constrainer`+`State` pair appropriate to what's being
  generated: a `TrieState` over encoded function names for `generate_name()`, and per-parameter-type states
  (`IntState`/`FloatState`/`StringState`/bool `TrieState`) built fresh for each parameter in `generate_parameters()`.
  Completions are trimmed at the first unescaped `"` (`__strip_completion`) since values are decoded as quoted
  JSON strings regardless of type, then parsed back into the target Python type.

When adding a new parameter type or output shape, the pattern is: add a `ParameterType` enum value
(`src/models/function.py`), add/extend a `State` for it, wire it into `GeneratorImpl.generate_parameters`'s
type dispatch, and update the final type-coercion switch in `CallMeMaybe.__process_prompt`.

### Supporting layers

- `src/parsing/` — `ArgumentParser` (argparse → pydantic `Arguments`), raises `ParsingError`/`ParsingValidationError`.
- `src/adapter/` — `JSONAdapter` wraps `json.dumps`/`json.loads`, converting `JSONDecodeError` into
  `SerializationException`/`DeserializationException`.
- `src/tokenize/` — thin `Tokenizer` ABC over `Model.encode`/`decode` (kept swappable per the subject's bonus
  requirement to eventually stop depending on the SDK's `encode`/`decode` and rebuild tokenization from
  `get_logits_from_input_ids`/`get_path_to_vocab_file` alone).
- `src/prompting/` — builds the Qwen chat-template-style prompt strings (`__templates.py`) fed to the model for
  name selection and each parameter in turn, threading the previously generated parameter as context.

## Claude-authored reports

Reports (audits, reviews, etc.) written by Claude go under `claude/reports/`, named
`report_[number]_[timestamp].md` — `number` is a sequential index starting at 0, `timestamp` is
`YYYYMMDD-HHMMSS` (local time at creation). Example: `claude/reports/report_0_20260823-193657.md`.
This directory is tracked in git (not ignored).

## Working guidelines

- Never generate code unless directly asked to do so.
- When generating code, follow flake8's norm. Run `make lint-strict` (flake8 + mypy) to check compliance before
  considering a change done.
- Never use emojis — not in code, comments, markdown, or anywhere else.

## Constraints from the assignment spec (do not violate)

- Must work with `Qwen/Qwen3-0.6B`; other models are allowed only in addition to, not instead of, that one.
- No use of `dspy`, `pytorch`/`torch` model internals beyond what `llm_sdk` exposes, `huggingface`/`transformers`,
  `outlines`, or similar constrained-decoding/inference libraries — the constrained decoding itself must be
  hand-rolled against `llm_sdk`'s public surface (`get_logits_from_input_ids`, `get_path_to_vocab_file`, `encode`,
  optional `decode`). Private `llm_sdk` methods/attributes are off-limits.
- Function selection must come from the LLM's constrained generation, never from heuristics/string-matching.
- All pydantic classes for data validation; `numpy`/`json` are fine to use.
- Output (`data/output/<file>.json`) must always be a JSON array of `{prompt, name, parameters}` objects with
  exactly those keys, types matching `functions_definition.json`, no extras — 100% parseable, no crashes on
  malformed/missing input files.
- `data/output/` is git-ignored and must not be committed; `private/` is also git-ignored.
