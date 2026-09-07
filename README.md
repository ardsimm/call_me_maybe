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
- Writes every result as `{prompt, name, parameters}` to an output JSON file. A prompt whose
  generation fails is reported and skipped rather than aborting the batch, so it contributes no
  entry and the output can be shorter than the input.

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
writes the results to `data/output/function_calling_results.json`. The first run downloads and
caches `Qwen/Qwen3-0.6B` from the Hugging Face Hub.

The prompt templates the model is fed live in the top-level `templates/` directory (one
subdirectory per generation step, `function_names/` and `function_parameters/`), read relative to
the working directory the program is launched from. They are part of the program, not of the
`data/` inputs it is pointed at, and are not CLI-overridable.

To use custom paths, run the module directly instead:

```sh
uv run python -m src \
  --functions_definition <path/to/functions_definition.json> \
  --input <path/to/prompts.json> \
  --output <path/to/output.json>
```

All three flags are optional and independently overridable; any omitted one falls back to its
default. `--output` accepts any path and creates missing parent directories as needed. The model
(`Qwen/Qwen3-0.6B`) is fixed and not CLI-overridable, per the subject's requirement.

### Build

```sh
make build       # wraps src into an executable ./call_me_maybe
make build-test  # wraps tests into an executable ./run_tests
```

Each rule writes a small `chmod +x` shell script (`#!/usr/bin/env bash`, `cd`s to its own location,
then `exec uv run python -m <src|tests> "$@"`) so the tool/test suite can be invoked directly as a
standalone command, e.g. `./call_me_maybe --input <path>` or `./run_tests`, without prefixing
`uv run python -m` every time. `uv` still manages the venv/dependencies underneath — these are thin
wrappers, not standalone binaries. Neither script is committed; both are generated build artifacts
(git-ignored) and removed by `make clean`/`fclean`.

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

### Rebuild / reinstall

```sh
make re        # remove and regenerate ./call_me_maybe
make re-test   # remove and regenerate ./run_tests
make re-deps   # fclean + install: full dependency reinstall
```

### Clean

```sh
make clean    # remove __pycache__ / .mypy_cache / test output logs / the two build wrappers
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
  `Constrainer` pair for whatever is being generated next, up to a hard cap of 67 tokens per value
  as a safety net.

A failure during generation is one of two kinds, and the split decides how much of the run
survives it. A `GenerationError` is local to one prompt (a forbidden token picked, a generated name
matching no known function): it is caught per prompt, logged, and that prompt is skipped, so the
output file simply carries no entry for it and the rest of the batch still runs. A
`FatalGenerationError` means no prompt could ever succeed — the vocab file behind
`string_end_sequences` is unreadable, or the `templates/` files are missing — so it propagates all
the way up to `CallMeMaybe.run`, which reports it and abandons the run without writing any output.

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
- **A hard per-value token cap (`GeneratorImpl.TOKEN_GEN_LIMIT = 67`).** Every `State` is expected
  to eventually signal completion on its own, but a cap guards against one that doesn't, keeping
  the "reasonable speed" requirement true by construction rather than by trusting every grammar.
- **`Tokenizer` as its own swappable abstraction**, rather than calling `Model.encode`/`.decode`
  directly everywhere. Kept thin on purpose: the subject's bonus track asks for eventually rebuilding
  tokenization from `get_logits_from_input_ids`/`get_path_to_vocab_file` alone, without depending on
  the SDK's `encode`/`decode` — this seam is where that would slot in.
- **Pydantic for every data-carrying class** (`Arguments`, `Function`, `Parameter`, `Returns`,
  `PromptEntry`, `Context`), per the subject's hard requirement.
- **Input validation is pydantic's job, not hand-written code's.** Both input files are read, decoded
  with `pydantic_core.from_json`, and handed straight to `Context.model_validate`, which is the only
  thing that decides whether they are well-formed. `model_config = ConfigDict(extra="forbid")` on
  every model in `src/models/context.py` is what makes an unexpected key anywhere in either file a
  validation error, and a declared `type` outside `ParameterType` is rejected by the enum itself.
  This replaced a long hand-rolled checking routine that walked both files key by key, accumulating
  error strings — the same guarantees, in a fraction of the code, and with pydantic's own error
  messages naming the exact offending path. Only two rules can't be expressed as a schema and are
  still checked by hand afterwards, in `CallMeMaybe.__get_context`: that a non-empty prompts file
  isn't paired with an empty functions file, and copying each parameter's key into its
  `Parameter.name` (a parameter is keyed by its name in the JSON, so its own name isn't a field it
  can be validated from).
- **All the models in one module.** `Function`, `Parameter`, `ParameterType`, `Returns` and
  `PromptEntry` live alongside `Context` in `src/models/context.py` rather than in a separate
  `function.py`: they exist to describe exactly the two files a `Context` is built from, so
  splitting them across modules only obscured that they are one schema.
- **`Function.parameters` is a dict, not a list.** It mirrors the input file's own shape — an object
  keyed by parameter name — so validation is a direct structural match instead of a translation
  step, while insertion order still gives generation the declaration order it needs.

## Performance analysis

All numbers below come from the scenario batch included in this project.

You can reproduce them on your machine with

```sh
make test
```

A report will be generated and written to `/tests/test-reports`

> The scenario set runs **68 prompts**, of which **9 are excluded from the accuracy tally**: 8
> are genuinely ambiguous or adversarial with no single correct answer, and 1 is a prompt
> injection attempt that the program refuses outright rather than generating for. That leaves
> **59 graded prompts** carrying **117 parameters**.

- **Function name accuracy: 96.6%** (57/59 graded prompts)
- **Parameter accuracy: 88.0%** (103/117 parameters)
- **Malformed-input robustness: 17/17** fixtures rejected cleanly, with a clear message and no
  crash.
- **100% valid JSON, always.** Structural validity is guaranteed by construction, not by luck — a
  forbidden token can never be selected in the first place.
- **Speed**: the full default `data/input/function_calling_tests.json` **(11 prompts)** completes
  in about **12 seconds** end to end on a CUDA GPU (model load included), and the whole scenario
  set (68 prompts) finishes in **121 seconds** — comfortably inside the "under 5 minutes"
  requirement.

**These figures come from a desktop machine with a CUDA GPU; speed depends heavily on hardware.**
The same default batch takes **111 seconds on CPU only** (20 cores), i.e. roughly 10 s/prompt
against 1 s/prompt on GPU, so the 5-minute budget is the binding constraint somewhere around 30
prompts on a CPU-only machine.

The graded set deliberately includes scenarios built around the known weak paths below rather
than only happy-path prompts, so the parameter figure is a floor, not a showcase: function-name
selection is 100% on every non-adversarial scenario, and parameter accuracy is 100% on
`multi_param_types` (43/43) and 96.3% on `new_functions` (26/27).

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

*The following tests will not be included in the submit for this project but can be recovered from [the gihub repository](https://github.com/ardsimm/call_me_maybe)*

- **`tests/test_cases/`** — one subdirectory per scenario, each a self-contained
  `functions_definition.json` + `function_calling_tests.json` pair meant to be passed straight to
  `src` (`tests/test_cases/manifest.md` lists every scenario with its exact run command):
  - Happy-path scenarios stress multi-parameter functions spanning every `ParameterType`, edge-case
    values (negatives, zero, many-digit decimals, empty/whitespace strings, quotes, emoji, non-ASCII
    text), deliberately ambiguous or adversarial prompts (including prompt-injection attempts), and
    brand-new function domains never seen elsewhere in the test data.
  - **`malformed_inputs/`** pairs each bad input file (invalid JSON, missing/extra keys, wrong
    types, a parameter type outside the schema, empty functions/prompts, a missing file entirely)
    with an otherwise-valid counterpart, to isolate one failure mode at a time and confirm the
    program never crashes on it — no crash, a clear message, a graceful exit, per the subject's
    error-handling requirements.
- **`tests/__main__.py`** (`make test`) automates running every scenario above and grading the
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
    robustness, plus a full per-prompt pass/fail table — is written to `tests/test-reports/`, one
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
and writes an array of `{prompt, name, parameters}` objects to
`data/output/function_calling_results.json`, one entry per successfully generated prompt, e.g.:

```json
[
  {
    "prompt": "What is the sum of 40 and 2?",
    "name": "fn_add_numbers",
    "parameters": { "a": 40.0, "b": 2.0 }
  }
]
```

To run against custom functions/prompts:

```sh
uv run python -m src \
  --functions_definition tests/test_cases/multi_param_types/functions_definition.json \
  --input tests/test_cases/multi_param_types/function_calling_tests.json \
  --output data/output/multi_param_types.json
```

Or, after `make build`, the same thing via the standalone wrapper:

```sh
./call_me_maybe \
  --functions_definition tests/test_cases/multi_param_types/functions_definition.json \
  --input tests/test_cases/multi_param_types/function_calling_tests.json \
  --output data/output/multi_param_types.json
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

To grade the implementation's accuracy against every scenario under `tests/test_cases/` and write
a fresh report to `tests/test-reports/`:

```sh
make test
```

Or, after `make build-test`, via the standalone wrapper: `./run_tests`.
