"""Runs every JSON test-case scenario and reports name/parameter accuracy.

For each subdirectory of `claude/test_cases/` that has an
`expected_results.json`, runs `python -m src` against its
`functions_definition.json`/`function_calling_tests.json` pair and
compares the output to the expected function name and parameter values,
one entry per prompt in matching order. An expected entry with
`"skip": true` (a genuinely ambiguous or adversarial prompt with no
single correct answer) is run but excluded from the accuracy tally.

Separately, every fixture pair under `claude/test_cases/malformed_inputs/`
is run to check that malformed input never crashes the program (exit
code 0), per the subject's "no crash, graceful exit" requirement.

A markdown report is written to `claude/test-reports/`, and a short
summary is printed to stdout. No unit test framework is used -- this is
a plain script driving the CLI exactly like a human tester would.
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
TEST_CASES_DIR = ROOT / "tests" / "test_cases"
MALFORMED_DIR = TEST_CASES_DIR / "malformed_inputs"
REPORTS_DIR = ROOT / "tests" / "test-reports"
STDOUT = ROOT / "outputs" / "last_run_stdout.log"

JSONObject = Dict[str, object]


@dataclass
class ParameterCheck:
    name: str
    expected: object
    actual: Optional[object]
    correct: bool


@dataclass
class PromptCheck:
    prompt: str
    expected_name: str
    actual_name: str
    name_correct: bool
    skipped: bool
    parameter_checks: List[ParameterCheck]


@dataclass
class ScenarioReport:
    scenario: str
    prompt_checks: List[PromptCheck]


@dataclass
class MalformedCase:
    name: str
    description: str
    functions_definition: Path
    input_path: Path
    output_path: Path


@dataclass
class RobustnessCheck:
    description: str
    returncode: int
    passed: bool


MALFORMED_CASES: List[MalformedCase] = [
    MalformedCase(
        "invalid_syntax",
        "Invalid JSON syntax (trailing comma)",
        MALFORMED_DIR / "invalid_json.json",
        MALFORMED_DIR / "valid_minimal_prompts.json",
        MALFORMED_DIR / "output/invalid_syntax.json",
    ),
    MalformedCase(
        "missing_returns",
        "Missing 'returns' key",
        MALFORMED_DIR / "functions_missing_returns.json",
        MALFORMED_DIR / "valid_minimal_prompts.json",
        MALFORMED_DIR / "output/missing_returns.json",
    ),
    MalformedCase(
        "extra_top_level_key",
        "Extra top-level key on a function",
        MALFORMED_DIR / "functions_extra_key.json",
        MALFORMED_DIR / "valid_minimal_prompts.json",
        MALFORMED_DIR / "output/extra_top_level_key.json",
    ),
    MalformedCase(
        "functions_wrong_types",
        "Wrong types for description/parameters",
        MALFORMED_DIR / "functions_wrong_types.json",
        MALFORMED_DIR / "valid_minimal_prompts.json",
        MALFORMED_DIR / "output/functions_wrong_types.json",
    ),
    MalformedCase(
        "functions_bad_parameters",
        "Parameter type outside the ParameterType enum",
        MALFORMED_DIR / "functions_bad_parameter_type.json",
        MALFORMED_DIR / "valid_minimal_prompts.json",
        MALFORMED_DIR / "output/functions_bad_parameters.json",
    ),
    MalformedCase(
        "functions_empty",
        "Zero functions available at all",
        MALFORMED_DIR / "functions_empty.json",
        MALFORMED_DIR / "valid_minimal_prompts.json",
        MALFORMED_DIR / "output/functions_empty.json",
    ),
    MalformedCase(
        "missing_prompt",
        "Prompt object missing the 'prompt' key",
        MALFORMED_DIR / "valid_minimal_functions.json",
        MALFORMED_DIR / "prompts_missing_prompt_key.json",
        MALFORMED_DIR / "output/missing_prompt.json",
    ),
    MalformedCase(
        "prompts_non_string",
        "Prompt value is not a string",
        MALFORMED_DIR / "valid_minimal_functions.json",
        MALFORMED_DIR / "prompts_non_string.json",
        MALFORMED_DIR / "output/prompts_non_string.json",
    ),
    MalformedCase(
        "prompts_extra_key",
        "Extra key on a prompt object",
        MALFORMED_DIR / "valid_minimal_functions.json",
        MALFORMED_DIR / "prompts_extra_key.json",
        MALFORMED_DIR / "output/prompts_extra_key.json",
    ),
    MalformedCase(
        "prompts_empty_array",
        "Zero prompts at all (valid empty array)",
        MALFORMED_DIR / "valid_minimal_functions.json",
        MALFORMED_DIR / "prompts_empty_array.json",
        MALFORMED_DIR / "output/prompts_empty_array.json",
    ),
    MalformedCase(
        "does_not_exist",
        "Missing functions_definition file entirely",
        MALFORMED_DIR / "does_not_exist.json",
        MALFORMED_DIR / "valid_minimal_prompts.json",
        MALFORMED_DIR / "output/does_not_exist.json",
    ),
]


def load_json_array(path: Path) -> List[JSONObject]:
    """Load a JSON file expected to contain an array of objects.

    Parameters
    ----------
    path : Path
        The JSON file to load.

    Returns
    -------
    list of dict
        The parsed array.
    """
    with open(path) as file:
        data: List[JSONObject] = json.load(file)
    return data


def run_program(
    functions_definition: Path,
    input_path: Path,
    output_path: Path,
    stdout: Path,
    stderr: Path,
) -> int:
    """Run `python -m src` against a functions/prompts pair.

    Parameters
    ----------
    functions_definition : Path
        The functions-definition JSON file to pass as `--functions_definition`.
    input_path : Path
        The prompts JSON file to pass as `--input`.
    output_path : Path
        The output path to pass as `--output`.

    Returns
    -------
    int
        The process's exit code.
    """
    stdout.parent.mkdir(exist_ok=True, parents=True)
    stderr.parent.mkdir(exist_ok=True, parents=True)
    with open(stdout, "w") as stdout_file, open(stderr, "w") as stderr_file:
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "src",
                "--functions_definition",
                str(functions_definition),
                "--input",
                str(input_path),
                "--output",
                str(output_path),
            ],
            cwd=ROOT,
            stdout=stdout_file,
            stderr=stderr_file,
        )
    return result.returncode


def values_match(expected: object, actual: Optional[object]) -> bool:
    """Compare an expected parameter value to a generated one.

    Numeric values are compared with a small tolerance (rather than
    exact equality) since floats are round-tripped through string
    generation. Booleans are compared before the numeric case since
    `bool` is a subclass of `int` in Python.

    Parameters
    ----------
    expected : object
        The ground-truth value.
    actual : object, optional
        The value produced by the program, or None if missing entirely.

    Returns
    -------
    bool
        Whether the two values are considered equal.
    """
    if actual is None:
        return False
    if isinstance(expected, bool) or isinstance(actual, bool):
        return expected is actual
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(expected) - float(actual)) < 1e-6
    return expected == actual


def evaluate_scenario(scenario_dir: Path) -> Optional[ScenarioReport]:
    """Run one scenario and grade its output against its expected results.

    Parameters
    ----------
    scenario_dir : Path
        A subdirectory of `claude/test_cases/` containing
        `functions_definition.json`, `function_calling_tests.json`, and
        `expected_results.json`.

    Returns
    -------
    ScenarioReport or None
        The graded results, or None if `scenario_dir` has no
        `expected_results.json` (not an accuracy scenario).
    """
    expected_path = scenario_dir / "expected_results.json"
    if not expected_path.exists():
        return None

    functions_definition = scenario_dir / "functions_definition.json"
    input_path = scenario_dir / "function_calling_tests.json"
    run_program(
        functions_definition,
        input_path,
        ROOT / "tests" / "output" / f"{scenario_dir.name}.json",
        ROOT / "tests" / "stdout" / f"{scenario_dir.name}_stdout.log",
        ROOT / "tests" / "stderr" / f"{scenario_dir.name}_stderr.log",
    )

    prompts = load_json_array(input_path)
    expected_items = load_json_array(expected_path)
    actual_items = load_json_array(
        ROOT / "tests" / "output" / f"{scenario_dir.name}.json"
    )

    prompt_checks: List[PromptCheck] = []
    for prompt_obj, expected, actual in zip(
        prompts, expected_items, actual_items
    ):
        prompt = str(prompt_obj.get("prompt", ""))
        skipped = bool(expected.get("skip", False))
        expected_name = str(expected.get("name", ""))
        actual_name = str(actual.get("name", ""))
        name_correct = expected_name == actual_name

        expected_parameters_raw: object = expected.get("parameters", {})
        expected_parameters: JSONObject = (
            expected_parameters_raw
            if isinstance(expected_parameters_raw, dict)
            else {}
        )
        actual_parameters_raw: object = actual.get("parameters", {})
        actual_parameters: JSONObject = (
            actual_parameters_raw
            if isinstance(actual_parameters_raw, dict)
            else {}
        )

        parameter_checks: List[ParameterCheck] = []
        for key, expected_value in expected_parameters.items():
            actual_value = actual_parameters.get(key)
            correct = name_correct and values_match(
                expected_value, actual_value
            )
            parameter_checks.append(
                ParameterCheck(key, expected_value, actual_value, correct)
            )

        prompt_checks.append(
            PromptCheck(
                prompt=prompt,
                expected_name=expected_name,
                actual_name=actual_name,
                name_correct=name_correct,
                skipped=skipped,
                parameter_checks=parameter_checks,
            )
        )

    report = ScenarioReport(
        scenario=scenario_dir.name, prompt_checks=prompt_checks
    )

    graded = [check for check in report.prompt_checks if not check.skipped]
    skipped_count = len(report.prompt_checks) - len(graded)
    name_correct = sum(1 for check in graded if check.name_correct)
    param_checks = [
        parameter_check
        for check in graded
        for parameter_check in check.parameter_checks
    ]
    param_checks_len = len(param_checks)
    param_correct = sum(1 for p in param_checks if p.correct)
    graded_len = len(graded)

    print("========================================================")
    print(f"Ran {graded_len} prompt" + ("s" if graded_len > 1 else ""))
    print(f"Ignored {skipped_count} prompts")
    print(
        f"{name_correct}/{graded_len} name"
        + ("s" if name_correct > 1 else "")
        + " correct",
        f"({
            (
                100 * name_correct / graded_len
                if graded_len > 0
                else 0.0
            ):.2f
        }%)"
    )
    if param_checks_len:
        print(
            f"{param_correct}/{param_checks_len} params correct",
            f"({
                (
                    100 * param_correct / param_checks_len
                    if param_checks_len > 0
                    else 0.0
                ):.2f
            }%)"
        )
    print("========================================================")
    print("========================================================")

    return report


def evaluate_robustness() -> List[RobustnessCheck]:
    """Run every `malformed_inputs` fixture and check it doesn't crash.

    Returns
    -------
    list of RobustnessCheck
        One entry per `MALFORMED_CASES` entry.
    """
    checks: List[RobustnessCheck] = []
    for case in MALFORMED_CASES:
        returncode = run_program(
            case.functions_definition,
            case.input_path,
            case.output_path,
            ROOT
            / "tests"
            / "stdout"
            / f"malformed_cases_{case.name}_stdout.log",
            ROOT
            / "tests"
            / "stderr"
            / f"malformed_cases_{case.name}_stderr.log",
        )
        checks.append(
            RobustnessCheck(case.description, returncode, returncode == 0)
        )
    return checks


def percentage(numerator: int, denominator: int) -> str:
    """Format `numerator / denominator` as a percentage string.

    Parameters
    ----------
    numerator : int
        The count of correct/passing items.
    denominator : int
        The total count graded.

    Returns
    -------
    str
        `"n/a"` if `denominator` is 0, else a `"XX.X%"` string.
    """
    if denominator == 0:
        return "n/a"
    return f"{numerator / denominator * 100:.1f}%"


def render_scenario_section(report: ScenarioReport) -> List[str]:
    """Render one scenario's accuracy breakdown as markdown lines.

    Parameters
    ----------
    report : ScenarioReport
        The scenario's graded prompt checks.

    Returns
    -------
    list of str
        Markdown lines for this scenario's section.
    """
    graded = [check for check in report.prompt_checks if not check.skipped]
    skipped_count = len(report.prompt_checks) - len(graded)
    name_correct = sum(1 for check in graded if check.name_correct)
    param_checks = [
        parameter_check
        for check in graded
        for parameter_check in check.parameter_checks
    ]
    param_correct = sum(1 for p in param_checks if p.correct)

    lines: List[str] = [f"### {report.scenario}", ""]
    lines.append(
        f"- Name accuracy: {name_correct}/{len(graded)}"
        f" ({percentage(name_correct, len(graded))})"
    )
    lines.append(
        f"- Parameter accuracy: {param_correct}/{len(param_checks)}"
        f" ({percentage(param_correct, len(param_checks))})"
    )
    if skipped_count:
        lines.append(
            f"- Skipped (ambiguous, no ground truth): {skipped_count}"
        )
    lines.append("")
    lines.append("| Prompt | Expected name | Actual name | Result |")
    lines.append("| --- | --- | --- | --- |")
    for check in report.prompt_checks:
        prompt_preview = check.prompt.replace("|", "\\|")
        if len(prompt_preview) > 60:
            prompt_preview = prompt_preview[:57] + "..."
        if check.skipped:
            status = "skipped"
        elif check.name_correct and all(
            p.correct for p in check.parameter_checks
        ):
            status = "pass"
        else:
            status = "fail"
        lines.append(
            f"| {prompt_preview} | {check.expected_name} |"
            f" {check.actual_name} | {status} |"
        )
        if status == "fail":
            for parameter_check in check.parameter_checks:
                if not parameter_check.correct:
                    lines.append(
                        f"| &nbsp;&nbsp;`{parameter_check.name}` expected"
                        f" `{parameter_check.expected!r}`, got"
                        f" `{parameter_check.actual!r}` | | | |"
                    )
    lines.append("")
    return lines


def render_robustness_section(checks: List[RobustnessCheck]) -> List[str]:
    """Render the malformed-input robustness results as markdown lines.

    Parameters
    ----------
    checks : list of RobustnessCheck
        The results from `evaluate_robustness`.

    Returns
    -------
    list of str
        Markdown lines for the robustness section.
    """
    passed = sum(1 for check in checks if check.passed)
    lines: List[str] = [
        "## Malformed-input robustness",
        "",
        f"{passed}/{len(checks)} fixtures exited cleanly (no crash).",
        "",
        "| Case | Exit code | Result |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        status = "pass" if check.passed else "fail"
        lines.append(
            f"| {check.description} | {check.returncode} | {status} |"
        )
    lines.append("")
    return lines


def main() -> int:
    """Run every scenario/robustness fixture and write a report.

    Returns
    -------
    int
        Always 0; failures are reported, not treated as a script error.
    """
    scenario_dirs = sorted(
        path
        for path in TEST_CASES_DIR.iterdir()
        if path.is_dir() and path != MALFORMED_DIR
    )

    scenario_reports: List[ScenarioReport] = []
    for scenario_dir in scenario_dirs:
        print("\n========================================================")
        print("========================================================")
        print(f"Running scenario: {scenario_dir.name}...")
        report = evaluate_scenario(scenario_dir)
        if report is not None:
            scenario_reports.append(report)

    print("Running malformed-input robustness checks...")
    robustness_checks = evaluate_robustness()

    all_graded = [
        check
        for report in scenario_reports
        for check in report.prompt_checks
        if not check.skipped
    ]
    all_param_checks = [
        parameter_check
        for check in all_graded
        for parameter_check in check.parameter_checks
    ]
    total_name_correct = sum(1 for check in all_graded if check.name_correct)
    total_param_correct = sum(1 for p in all_param_checks if p.correct)
    robustness_passed = sum(1 for check in robustness_checks if check.passed)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"report_{timestamp}.md"

    lines: List[str] = [
        f"# Test report -- {timestamp}",
        "",
        "## Summary",
        "",
        f"- Function name accuracy: {total_name_correct}/{len(all_graded)}"
        f" ({percentage(total_name_correct, len(all_graded))})",
        f"- Parameter extraction accuracy:"
        f" {total_param_correct}/{len(all_param_checks)}"
        f" ({percentage(total_param_correct, len(all_param_checks))})",
        f"- Malformed-input robustness:"
        f" {robustness_passed}/{len(robustness_checks)}",
        "",
        "## Scenarios",
        "",
    ]
    for report in scenario_reports:
        lines.extend(render_scenario_section(report))
    lines.extend(render_robustness_section(robustness_checks))

    report_path.write_text("\n".join(lines))

    print()
    print(
        f"Function name accuracy: {total_name_correct}/{len(all_graded)}"
        f" ({percentage(total_name_correct, len(all_graded))})"
    )
    print(
        f"Parameter extraction accuracy:"
        f" {total_param_correct}/{len(all_param_checks)}"
        f" ({percentage(total_param_correct, len(all_param_checks))})"
    )
    print(
        f"Malformed-input robustness:"
        f" {robustness_passed}/{len(robustness_checks)}"
    )
    print(f"\nFull report written to {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
