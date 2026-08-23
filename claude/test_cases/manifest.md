# Test case manifest

Each subdirectory is a `functions_definition.json` + `function_calling_tests.json` pair meant to be
run directly against `src` (not submitted/graded, per the subject's "Additional Guidelines").

Note: as of commit `eafca7a` ("fix: allow output file to go in any directory"), `--output` accepts
a full path (parent directories are created automatically), so the commands below pass a path
under `data/output/` directly.

## Happy-path scenarios

```sh
uv run python -m src \
  --functions_definition claude/test_cases/multi_param_types/functions_definition.json \
  --input claude/test_cases/multi_param_types/function_calling_tests.json \
  --output data/output/multi_param_types.json

uv run python -m src \
  --functions_definition claude/test_cases/edge_values/functions_definition.json \
  --input claude/test_cases/edge_values/function_calling_tests.json \
  --output data/output/edge_values.json

uv run python -m src \
  --functions_definition claude/test_cases/ambiguous_and_adversarial/functions_definition.json \
  --input claude/test_cases/ambiguous_and_adversarial/function_calling_tests.json \
  --output data/output/ambiguous_and_adversarial.json
```

- `multi_param_types`: functions with 4-5 parameters spanning every `ParameterType`
  (`int`, `number`, `boolean`, `string`) in a single call, including the `int` type which never
  appears in the default `data/input/functions_definition.json`.
- `edge_values`: negative numbers, zero, many-digit decimals, a number far larger than fits a
  64-bit int, empty strings, quotes/apostrophes/percent signs, non-ASCII text and emoji, and
  literal `\n`/`\t` inside a string.
- `ambiguous_and_adversarial`: vague prompts with no clearly-correct function, prompts that
  straddle two functions at once, gibberish, and prompt-injection attempts (fake chat-template
  turns, "ignore previous instructions").

## Error-handling scenarios (malformed_inputs/)

Each bad file is paired with `valid_minimal_functions.json` / `valid_minimal_prompts.json` to
isolate one failure mode at a time. Expected behavior per the subject (IV.3.1, V.5): no crash,
a clear message, graceful exit.

```sh
# Invalid JSON syntax (trailing comma) -> Arguments.validate_model's json.JSONDecodeError branch
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/invalid_json.json \
  --input claude/test_cases/malformed_inputs/valid_minimal_prompts.json \
  --output data/output/malformed_invalid_json.json

# Missing "returns" key
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/functions_missing_returns.json \
  --input claude/test_cases/malformed_inputs/valid_minimal_prompts.json \
  --output data/output/malformed_missing_returns.json

# Extra top-level key (5 entries instead of 4)
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/functions_extra_key.json \
  --input claude/test_cases/malformed_inputs/valid_minimal_prompts.json \
  --output data/output/malformed_extra_key.json

# Wrong types for description/parameters
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/functions_wrong_types.json \
  --input claude/test_cases/malformed_inputs/valid_minimal_prompts.json \
  --output data/output/malformed_wrong_types.json

# Parameter type outside the ParameterType enum ("array")
# This one is a real unhandled ValueError (Context.__init__ builds
# Parameter(type=ParameterType(value["type"])) with no try/except) -- caught only by
# __main__.py's blanket handler, which prints a traceback but still exits 0 with no output file.
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/functions_bad_parameter_type.json \
  --input claude/test_cases/malformed_inputs/valid_minimal_prompts.json \
  --output data/output/malformed_bad_parameter_type.json

# Zero functions available at all
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/functions_empty.json \
  --input claude/test_cases/malformed_inputs/valid_minimal_prompts.json \
  --output data/output/malformed_empty_functions.json

# Prompt object missing the "prompt" key
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/valid_minimal_functions.json \
  --input claude/test_cases/malformed_inputs/prompts_missing_prompt_key.json \
  --output data/output/malformed_missing_prompt_key.json

# Prompt value is not a string
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/valid_minimal_functions.json \
  --input claude/test_cases/malformed_inputs/prompts_non_string.json \
  --output data/output/malformed_prompt_non_string.json

# Extra key on a prompt object
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/valid_minimal_functions.json \
  --input claude/test_cases/malformed_inputs/prompts_extra_key.json \
  --output data/output/malformed_prompt_extra_key.json

# Zero prompts at all (valid empty array)
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/valid_minimal_functions.json \
  --input claude/test_cases/malformed_inputs/prompts_empty_array.json \
  --output data/output/malformed_empty_prompts.json

# Missing file entirely (no fixture needed)
uv run python -m src \
  --functions_definition claude/test_cases/malformed_inputs/does_not_exist.json \
  --input claude/test_cases/malformed_inputs/valid_minimal_prompts.json \
  --output data/output/malformed_missing_file.json
```
