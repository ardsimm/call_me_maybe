from typing import List, Dict, TypedDict
from src.models.arguments import Arguments
from src.models.function import Function, Parameter, ParameterType
from pydantic import BaseModel, Field
from src.parsing.parser_exceptions import ParsingError, ParsingValidationError
import json


class ParameterDict(TypedDict):
    type: str


class FunctionDict(TypedDict):
    name: str
    description: str
    parameters: Dict[str, ParameterDict]


class Context(BaseModel):
    functions: List[Function] = Field()
    prompts: List[str] = Field()

    def __init__(self, arguments: Arguments):
        super().__init__(prompts=[], functions=[])
        self.functions = []
        with open(arguments.functions_definition) as functions_definition:
            functions_dicts: List[FunctionDict] = json.loads(
                functions_definition.read()
            )
        for function_dict in functions_dicts:
            name = function_dict.get("name")
            description = function_dict.get("description")
            parameters = function_dict.get("parameters")
            returns = function_dict.get("returns")
            errors: List[str] = []
            if name is None:
                errors.append("Missing name in function")
            if description is None:
                errors.append("Missing description in function")
            if parameters is None:
                errors.append("Missing parameters in function")
            if returns is None:
                errors.append("Missing returns in function")
            if name is not None and not isinstance(name, str):
                errors.append("Invalid type for name in function")
            if description is not None and not isinstance(description, str):
                errors.append("Invalid type for description in function")
            if parameters is not None and not isinstance(parameters, dict):
                errors.append("Invalid type for parameters in function")
            if returns is not None and not isinstance(returns, dict):
                errors.append("Invalid type for returns in function")
            if (len(function_dict.items()) != 4):
                errors.append("To many entries in function")
            if (len(errors)):
                raise ParsingError(
                    "Missing or invalid fields in function:\n" + (
                        "\n".join(" - " + error for error in errors)
                    )
                )
            try:
                function = Function(
                    name=name,
                    description=description,
                    parameters=[
                        Parameter(name=key, type=ParameterType(value["type"]))
                        for key, value in parameters.items()
                    ],
                )
            except ValueError as err:
                raise ParsingError(f"Invalid parameter type: {err}")
            self.functions.append(function)
        with open(arguments.input) as prompts:
            prompts_dicts = json.loads(prompts.read())
            for prompt_dict in prompts_dicts:
                prompt = prompt_dict.get("prompt")
                if prompt is None or not isinstance(prompt, str):
                    raise ParsingError(
                        "Missing or invalid value in prompts file"
                    )
                if (len(prompt_dict.items()) != 1):
                    raise ParsingError("Too many entries in prompt")
                self.prompts.append(prompt)
