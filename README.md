*This project has been created as part of the 42 curriculum by smenard.*

# Call Me Maybe

## Description

Large language models are fluent at natural language, but they don't naturally produce structured,
machine-executable output. **Call Me Maybe** is a function-calling tool: it takes a
natural-language prompt and turns it into a concrete function call with typed arguments, instead of
just answering in prose.

```
Prompt: "What is the sum of 40 and 2?"

A regular LLM: "The sum of 40 and 2 is 42."

Call Me Maybe: {"name": "fn_add_numbers", "parameters": {"a": 40.0, "b": 2.0}}
```

Small language models are notoriously unreliable at producing valid structured output through
prompting alone — asked to output JSON, they might succeed only ~30% of the time. This project
does not prompt-and-hope: it implements **constrained decoding**, masking the model's logits at
every generation step so only tokens that keep the output structurally and schema-valid can ever
be picked. The result is close to 100% valid, schema-compliant JSON, even from a genuinely small
model (`Qwen/Qwen3-0.6B`, 500M parameters — other models are allowed in addition to it, but not
instead of it).

Concretely, the tool:

- Loads a set of available functions from a JSON file.
- Reads a list of natural-language prompts from another JSON file.
- Picks the right function per prompt and extracts its parameter values under constrained decoding.
- Writes every result as `{prompt, name, parameters}` to an output JSON file.

## Instructions

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for dependency management
- The `llm_sdk` package, provided alongside this project and already checked into this repository
  next to `src/`

### Install

```sh
make install
```

Runs `uv sync`, creating a `.venv` and installing all dependencies (`numpy`, `pydantic`, etc., plus
`llm_sdk` as an editable workspace member).

### Run

```sh
make run
```

Reads `data/input/functions_definition.json` and `data/input/function_calling_tests.json`, and
writes the results to `data/output/function_calls.json`. The first run downloads and caches
`Qwen/Qwen3-0.6B` from the Hugging Face Hub.

To use custom paths or a different model, run the module directly instead:

```sh
uv run python -m src \
  --functions_definition <path/to/functions_definition.json> \
  --input <path/to/prompts.json> \
  --output <path/to/output.json> \
  --model <hf-model-id>
```

All four flags are optional and independently overridable; any omitted one falls back to its
default. `--output` accepts any path and creates missing parent directories as needed.

### Debug

```sh
make debug
```

Runs the program under Python's `pdb` debugger.

### Lint

```sh
make lint         # flake8 + the subject-mandated mypy flags
make lint-strict   # flake8 + mypy --strict
```

### Clean

```sh
make clean    # remove __pycache__ / .mypy_cache
make fclean   # also remove the .venv
```

### Formatting
```sh
make black  # run the black formatter on every file in /src
```

## Resources

### References

- [Pydantic documentation](https://docs.pydantic.dev/) — data validation for every model in `src/models/`.
- [uv documentation](https://docs.astral.sh/uv/) — dependency management and the workspace setup used for `llm_sdk`.
- [Qwen3-0.6B model card](https://huggingface.co/Qwen/Qwen3-0.6B) — the default model.
- [JSON Schema](https://json-schema.org/) — background on the `type`/`parameters`/`returns` shape used in `functions_definition.json`.
- [Python `argparse` documentation](https://docs.python.org/3/library/argparse.html) — CLI argument parsing in `ArgumentParser`.

### How AI was used

- **Initial project jumpstart**: de-mystifying the core notions of the project (function calling,
  constrained decoding) and getting advice on the overall project structure before writing code.
- **Documentation**: writing the NumPy-style docstrings across `src/`, including tracing each
  function's call graph to document exceptions forwarded from its callees, not just the ones it
  raises itself.
- **Testing**: designing JSON test fixtures covering edge cases (multi-parameter functions,
  negative numbers, empty/special-character strings, ambiguous and adversarial prompts, malformed
  input files), running them, and measuring function-name/parameter accuracy.
- **Debugging aid**: diagnosing a handful of runtime crashes surfaced by that testing (an argument
  mismatch after a refactor, a typo in the boolean-parameter branch, a missing negative-number case
  in the number-generating states).
- **Code audit**: two passes over the codebase — an initial design/compliance review, and a
  follow-up exception-handling and dead-code review once the docstring pass had mapped out every
  call path.

## Algorithm explanation

Normal LLM decoding picks the highest-probability next token out of the entire vocabulary at every
step. **Constrained decoding** restricts that choice, at every single step, to only the tokens that
keep the output both syntactically valid and compliant with the expected schema — so the model is
structurally incapable of producing anything else, rather than merely being asked nicely to.

The pipeline for one prompt:

1. **Name generation.** The prompt (built from a chat-template, see `src/prompting/`) is tokenized,
   and a `TrieState` is built from every candidate function name, already tokenized. At each
   decoding step, the model's raw logits are fetched via `get_logits_from_input_ids`, and only the
   tokens that are children of the trie's current node are eligible — the model can only ever walk
   a path that spells out one of the real function names, character by character (in token form).
   Once a node has no children left, generation stops: the name is complete and guaranteed valid.
2. **Parameter generation**, one parameter at a time, each under a state matching its declared
   type:
   - `IntState` / `FloatState`: digit tokens only (plus an optional leading `-`, and `.` for
     floats), until a token that closes the value is picked.
   - `StringState`: any token is allowed, until an unescaped `"` is picked.
   - boolean parameters: another `TrieState`, built from only `"true"` and `"false"`.
   Every previously generated parameter is threaded back into the prompt as context for the next
   one, so later parameters can be informed by earlier ones.
3. Every generated value is decoded as if it were a quoted JSON string (trimmed at the first
   unescaped `"`), then parsed into its real Python type (`int`/`float`/`bool`/`str`) before being
   written out.

Each of the moving parts above maps to one layer of the codebase:

- `Model` (`src/model/model.py`) wraps `llm_sdk.Small_LLM_Model` and adds
  `string_end_sequences` — every vocab token whose text contains an unescaped `"`, computed once
  from the vocab file. This is what every state uses to know when a value/name is allowed to end.
- `State` (`src/state/`) is the grammar itself: a small state machine of `allowed_tokens` (what may
  be emitted now) and `transition_tokens` (which emitted tokens advance to the next stage).
- `Constrainer` (`src/constrainer/`) takes raw logits and a `State`, and picks
  `argmax(logits)` restricted to `state.get_allowed_tokens()` — this is the actual masking step.
- `Generator` (`src/generate/`) drives the token-by-token loop, swapping in the right `State`/
  `Constrainer` pair for whatever is being generated next, up to a hard cap of 500 tokens per value
  as a safety net.

## Design decisions

- **Restrict the candidate set instead of masking logits to `-inf`.** The subject frames constrained
  decoding as setting forbidden tokens' logits to negative infinity before sampling. This project
  gets the same guarantee more directly: `Constrainer.pick_token` takes `argmax` over only the
  tokens a `State` currently allows, so forbidden tokens are never in the running at all rather than
  being scored and then suppressed.
- **Every value is generated as a JSON string, regardless of its real type.** `int`/`float`/`bool`
  values are decoded exactly like strings — generated until an unescaped `"` appears — then parsed
  into their real type afterward. This lets every `State` share one termination convention
  (`string_end_sequences`) instead of each type needing its own closing rule.
- **Factories everywhere, mostly returning singletons.** `Model`, `AdapterFactory`,
  `TokenizerFactory`, `GeneratorFactory` all cache and return one shared instance, since there's
  only ever one model/tokenizer/adapter/generator per run; `StateFactory` and `ConstrainerFactory`
  return a fresh instance each time instead, since a state machine's whole point is to hold
  per-generation, mutable progress.
- **A hard per-value token cap (`GeneratorImpl.TOKEN_GEN_LIMIT = 500`).** Every `State` is expected
  to eventually signal completion on its own, but a cap guards against one that doesn't, keeping
  the "reasonable speed" requirement true by construction rather than by trusting every grammar.
- **`Tokenizer` as its own swappable abstraction**, rather than calling `Model.encode`/`.decode`
  directly everywhere. Kept thin on purpose: the subject's bonus track asks for eventually rebuilding
  tokenization from `get_logits_from_input_ids`/`get_path_to_vocab_file` alone, without depending on
  the SDK's `encode`/`decode` — this seam is where that would slot in.
- **Pydantic for every data-carrying class** (`Arguments`, `Function`, `Parameter`, `Context`), per
  the subject's hard requirement — field constraints (`min_length=1`, etc.) double as the first
  layer of input validation, before any file content is trusted.

## Performance analysis

All numbers below come from the batch of unit test included in this project 

You can run these tests on your machine with

```sh
make test
```

A report will be generated and written to `/claude/test-reports`

> The test cases include a prompt injection attempt that is skipped by the program. This prompt is ignored in the metrics given here since it cannot be properly processed with the tools available to us in this project.

- **Function name accuracy: 100%** (45/45 prompts with an objectively correct answer)
- **Parameter accuracy: 96%** (96/100 parameters)
- **100% valid JSON, always.** Structural validity is guaranteed by construction, not by luck — a
  forbidden token can never be selected in the first place.
- **Speed**: the full default `data/input/function_calling_tests.json` **(20 prompts)** completes in
  about **14 seconds** end to end (model load included), and every scenario in the **test set (45 prompts)** finished its
  batch in **99 seconds** (~ 1 minute and a half) — comfortably inside the "under 5 minutes" requirement 
  
**Again, these metrics come from tests executed on a desktop computer with a very powerful GPU, compute speed will greatly depend on hardware limitations**

Known remaining limitations:

- When a prompt doesn't actually specify a required argument (e.g. "make it really cold", no
  number given), the model still has to produce *something* for that parameter — there's no
  "unknown" value in the schema, so it fabricates a plausible-looking one.

## Challenges faced

<!-- Difficulties encountered and how they were solved. -->

- `Model.string_end_sequences` decides whether a token ends a JSON string purely by looking at that token's own text, with no awareness of the string generated so far -- this one design choice is the root cause behind most of the issues below, several of which are different symptoms of the same underlying gap:
  - A merged vocab token can smuggle a stray character (e.g. a trailing `-`) past `IntState`'s
    digit check, producing an otherwise-invalid numeral
  - `IntState` (and originally `FloatState`) had no mechanism forcing a digit after a leading `-`, so the model could in principle repeat `-` forever with no digit ever required
  - Numeric parameters could overflow to `Infinity`/`-Infinity` (not valid JSON) via scientific notation runaway digit generation, and the `<|im_end|>`/`<|im_start|>` prompt-injection guard was initially bypassable.

## Testing strategy

Per the subject's "Additional Guidelines", tests are for the author's own verification and are not
submitted or graded, so there is no unit test suite and no test framework (`pytest`, `unittest`,
etc.) anywhere in this repo. Verification instead runs the real CLI end to end against hand-written
JSON fixtures — the same way a user would actually invoke the program.

- **`claude/test_cases/`** — one subdirectory per scenario, each a self-contained
  `functions_definition.json` + `function_calling_tests.json` pair meant to be passed straight to
  `src` (`claude/test_cases/manifest.md` lists every scenario with its exact run command):
  - Happy-path scenarios stress multi-parameter functions spanning every `ParameterType`, edge-case
    values (negatives, zero, many-digit decimals, empty/whitespace strings, quotes, emoji, non-ASCII
    text), deliberately ambiguous or adversarial prompts (including prompt-injection attempts), and
    brand-new function domains never seen elsewhere in the test data.
  - **`malformed_inputs/`** pairs each bad input file (invalid JSON, missing/extra keys, wrong
    types, a parameter type outside the schema, empty functions/prompts, a missing file entirely)
    with an otherwise-valid counterpart, to isolate one failure mode at a time and confirm the
    program never crashes on it — no crash, a clear message, a graceful exit, per the subject's
    error-handling requirements.
- **`claude/run_tests.py`** (`make test`) automates running every scenario above and grading the
  result:
  - Each happy-path scenario is paired with an `expected_results.json` — the ground-truth
    `name`/`parameters` for every prompt, worked out by hand from what the prompt actually asks for,
    independently of what the model happens to output. Genuinely ambiguous or adversarial prompts
    with no single correct answer are marked `"skip": true`: still run, but excluded from the
    accuracy tally rather than graded against an arbitrary "correct" answer.
  - Every `malformed_inputs/` fixture is re-run and checked for a clean exit code, separately from
    the accuracy tally.
  - A markdown report — overall and per-scenario function-name accuracy, parameter accuracy (numeric
    values compared with a small tolerance rather than exact string equality), and malformed-input
    robustness, plus a full per-prompt pass/fail table — is written to `claude/test-reports/`, one
    timestamped file per run, so accuracy can be tracked over time as the implementation changes.
- Bugs surfaced by this testing were written up as GitHub-issue-style documents under
  `claude/issues/` (see "Challenges faced" above) with exact repro commands, rather than just fixed
  silently, so each one stays checkable against the running program later.

## Example usage

```sh
make install
make run
```

Reads the default `data/input/functions_definition.json` and `data/input/function_calling_tests.json`,
and writes an array of `{prompt, name, parameters}` objects to `data/output/function_calls.json`,
one entry per prompt, e.g.:

```json
[
  {
    "prompt": "What is the sum of 40 and 2?",
    "name": "fn_add_numbers",
    "parameters": { "a": 40.0, "b": 2.0 }
  }
]
```

To run against custom functions/prompts, or a different model:

```sh
uv run python -m src \
  --functions_definition claude/test_cases/multi_param_types/functions_definition.json \
  --input claude/test_cases/multi_param_types/function_calling_tests.json \
  --output data/output/multi_param_types.json \
  --model Qwen/Qwen3-0.6B
```

Given the prompt `"Book a flight to Tokyo for Alice Dupont, seat 42, price 350.5, with luggage"`,
this produces:

```json
{
  "prompt": "Book a flight to Tokyo for Alice Dupont, seat 42, price 350.5, with luggage",
  "name": "fn_book_flight",
  "parameters": {
    "passenger_name": "Alice Dupont",
    "seat_number": 42,
    "price": 350.5,
    "has_luggage": true,
    "destination": "Tokyo"
  }
}
```

To grade the implementation's accuracy against every scenario under `claude/test_cases/` and write
a fresh report to `claude/test-reports/`:

```sh
make test
```
