from pydantic import ValidationError
from src.parsing.parser_exceptions import ParsingError, ParsingValidationError
from .parser import Parser
from typing import List
from src.models import Arguments
from argparse import ArgumentParser as _ArgumentParser


class ArgumentParser(Parser):
    """`Parser` that reads CLI arguments via the standard `argparse` module."""

    def parse(self, source: List[str]) -> Arguments:
        """Parse `source` into an `Arguments`, overriding its defaults.

        Builds `Arguments` with its defaults first (which itself opens and
        validates the default input files), then overrides each field
        whose CLI flag was actually passed -- each override re-runs
        `Arguments.validate_model` against the new value, since
        `validate_assignment=True`.

        Parameters
        ----------
        source : list of str
            The raw CLI argument tokens (e.g. `sys.argv[1:]`).

        Returns
        -------
        Arguments
            The parsed, validated arguments.

        Raises
        ------
        ParsingValidationError
            If building or overriding `Arguments` raises
            `pydantic.ValidationError`.
        ParsingError
            Wraps any other exception raised while building `Arguments`
            (e.g. `OSError` or `DeserializationException` from
            `Arguments.validate_model` -- see its docstring).
        SystemExit
            Uncaught: `_ArgumentParser.parse_args` calls `sys.exit` on
            `--help` or an unrecognized argument. `SystemExit` is not an
            `Exception` subclass, so the `except Exception` below does not
            catch it.
        """
        parser: _ArgumentParser = _ArgumentParser(
            prog="Call Me Maybe",
        )

        parser.add_argument(
            "--functions_definition",
            help="The path to the JSON file containing functions definition",
            default=None,
        )
        parser.add_argument(
            "--input",
            help="The path to the JSON file containing the prompts",
            default=None,
        )
        parser.add_argument(
            "--output",
            help="The path to the JSON file to write the output of the LLM",
            default=None,
        )

        try:
            arguments = Arguments()
            parsed = parser.parse_args(source)
            if parsed.functions_definition is not None:
                arguments.functions_definition = parsed.functions_definition
            if parsed.input is not None:
                arguments.input = parsed.input
            if parsed.output is not None:
                arguments.output = parsed.output
        except ValidationError as e:
            validation_errors = e.errors()
            raise ParsingValidationError(validation_errors)
        except Exception as e:
            raise ParsingError(f"Parsing error {e}")
        return arguments
