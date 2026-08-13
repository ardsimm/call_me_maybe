from pydantic import ValidationError
from src.parsing.parser_exceptions import ParsingError, ParsingValidationError
from .parser import Parser
from typing import List
from src.models import Arguments
from argparse import ArgumentParser as _ArgumentParser


class ArgumentParser(Parser):

    def parse(self, source: List[str]) -> Arguments:
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
        parser.add_argument(
            "--model", help="The model to use for the generation", default=None
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
            if parsed.model is not None:
                arguments.model = parsed.model
        except ValidationError as e:
            validation_errors = e.errors()
            raise ParsingValidationError(validation_errors)
        except Exception as e:
            raise ParsingError(f"Parsing error {e}")
        return arguments
