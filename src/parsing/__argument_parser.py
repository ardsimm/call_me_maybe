from .parser import Parser
from typing import List
from src.models.arguments import Arguments
from argparse import ArgumentParser as _ArgumentParser


class ArgumentParser(Parser):

    def parse(self, source: List[str]) -> Arguments:
        parser: _ArgumentParser = _ArgumentParser(
            prog="Call Me Maybe",
        )
        arguments = Arguments()

        parser.add_argument(
            "--functions_definition",
            help="The path to the JSON file containing functions definition"
        )
        parser.add_argument(
            "--input",
            help="The path to the JSON file containing the prompts"
        )
        parser.add_argument(
            "--output",
            help="The path to the JSON file to write the output of the LLM",
        )
        parser.add_argument(
            "--model",
            help="The model to use for the generation",
        )

        parsed = parser.parse_args(source)
        if parsed.functions_definition is not None:
            arguments.functions_definition = parsed.functions_definition
        if parsed.input is not None:
            arguments.input = parsed.input
        if parsed.output is not None:
            arguments.output = parsed.output
        if parsed.model is not None:
            arguments.model = parsed.model
        return arguments
