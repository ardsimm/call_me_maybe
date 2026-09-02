# Accuracy Metrics Timeline

At-a-glance history of function-name and parameter-extraction accuracy across the session. Each
row links to its own small report in this directory, which links in turn to the full report under
`claude/reports/` (where one exists). Function name and parameter accuracy are only ever compared
apples-to-apples within the same scope (3 scenarios for the first two rows, 5 scenarios --
`multi_param_types`, `edge_values`, `ambiguous_and_adversarial`, `new_functions`,
`extreme_edge_cases` -- from `metrics_2` onward); the scope change is exactly where the jump in
prompt/parameter counts happens below.

| # | Milestone | Scope | Function name | Parameters |
|---|---|---|---|---|
| 0 | Baseline (`metrics_0`) | 25 prompts / 63 params | 24/25 = 96% | 58/63 = 92% |
| 1 | Quote-escaping + isolation fixes, Config B (`metrics_1`) | 25 prompts / 63 params | 24/25 = 96% | 61/63 = 97% |
| 2a | Suite expanded to 5 scenarios; `Infinity` bug found (`metrics_2`) | 45 prompts / 102 params | 44/45 = 98% | 99/102 = 97% |
| 2b | First `Infinity` fix (whole-prompt refusal) (`metrics_2`) | 45 prompts / 100 params | 43/45 = 96% | 99/100 = 99% |
| 3 | Revised `Infinity` fix (per-parameter fallback) (`metrics_3`) | 45 prompts / 102 params | 44/45 = 98% | 99/102 = 97% |
| 4 | Scientific notation support in `FloatState` (`metrics_4`) | 45 prompts / 102 params | 44/45 = 98% | 100/102 = 98% |
| 5 | Trailing/embedded minus-sign robustness (`metrics_5`) | 45 prompts / 102 params | 44/45 = 98% | 100/102 = 98% (unchanged) |
| 6 | **Speed milestone** - first four performance fixes (`metrics_6`) | 20-prompt hard set, timing only | not re-scored | not re-scored |

Row 6 is a **speed** milestone and deliberately carries no accuracy figures: the 45-prompt scored
suite was not re-run, so rows 0-5 remain the last measured accuracy. Its numbers are wall clock
(15 min -> 9:51 for 20 prompts), seconds per forward pass (1.986 -> 1.795), and wasted forward
passes (15.3% -> 0). One unscored defect was visible in its output -- a `recipient` value copied
verbatim out of a few-shot example -- which is why the next round of prompt trimming must restore
accuracy scoring rather than continue on timing alone.

## Reading the trend

- Parameter accuracy climbed from **92% to 98%** over the session (rows 0 -> 4), with one dip and
  recovery in between (rows 2b/3) caused entirely by two different strategies for handling the
  same overflow bug, not by any regression in extraction quality itself.
- Function name accuracy has stayed flat at 96-98% throughout; its only real "miss" for most of
  the session is the prompt-injection prompt, which went from a successful hijack (before
  `metrics_0`) to a safe refusal (from `metrics_0` onward) -- a change in *how* it fails, not
  reflected in the raw percentage.
- Rows 2a/2b/3 are the clearest illustration in this history of a general pattern: whether a
  gracefully-degraded case counts as a function-name hit-with-wrong-parameters or a
  function-name-miss-with-nothing-scored is a modeling choice in how the fix responds, and it
  trades points between the two metrics without changing the underlying quality of what's being
  measured. Read both numbers together, not in isolation.
- As of row 5, only two misses remain anywhere in the 45-prompt scored suite: the prompt-injection
  refusal (by design) and one still-open parameter miss (a 52-digit, no-decimal-point number that
  overflows via a separate, unrelated `FloatState` gap -- see `metrics_4`).
