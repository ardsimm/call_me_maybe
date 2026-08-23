from typing import List, Dict, TypedDict
from src.models.arguments import Arguments
from src.models.function import Function, Parameter, ParameterType
from pydantic import BaseModel, Field
from src.parsing.parser_exceptions import ParsingError
import json


class ParameterDict(TypedDict):
    """Raw shape of one parameter entry in `functions_definition.json`."""

    type: str


class FunctionDict(TypedDict):
    """Raw shape of one function entry in `functions_definition.json`."""

    name: str
    description: str
    parameters: Dict[str, ParameterDict]


class Context(BaseModel):
    """The loaded, validated set of functions and prompts for a run.

    Attributes
    ----------
    functions : list of Function
        The functions parsed from `arguments.functions_definition`.
    prompts : list of str
        The prompts parsed from `arguments.input`.
    """

    functions: List[Function] = Field()
    prompts: List[str] = Field()

    def __init__(self, arguments: Arguments):
        """Load and validate both input files referenced by `arguments`.

        Parameters
        ----------
        arguments : Arguments
            Supplies the paths to the functions-definition and prompts
            JSON files.

        Raises
        ------
        OSError
            If `arguments.functions_definition` or `arguments.input`
            cannot be opened.
        json.JSONDecodeError
            If either file's content is not valid JSON (parsed directly
            via `json.loads` here, not through `JSONAdapter`).
        ParsingError
            If a function entry is missing `name`/`description`/
            `parameters`/`returns`, has the wrong type for one of them, or
            has extra/missing top-level keys; or if a prompt entry is
            missing `prompt`, has a non-string value, or has extra keys.
        ValueError
            Uncaught, from `ParameterType(value["type"])`: if a
            parameter's `type` is not one of `ParameterType`'s values
            (e.g. `"array"`), this raises directly rather than being
            folded into the `ParsingError` convention used everywhere
            else in this method.
        TypeError
            Uncaught, from `value["type"]`: if a parameter's definition is
            not itself a dict (only the outer `parameters` dict is
            type-checked, not each entry), subscripting it raises this.
        pydantic.ValidationError
            Uncaught, from constructing `Function`/`Parameter`: this
            method only checks that `name`/`description` are strings, not
            that they are non-empty, so an empty one passes here and then
            fails `Function`/`Parameter`'s own `min_length=1` validation.
        """
        super().__init__(prompts=[], functions=[])
        self.functions = []
        try:
            with open(arguments.functions_definition) as functions_definition:
                functions_dicts: List[FunctionDict] = json.loads(
                    functions_definition.read()
                )
        except (OSError, json.JSONDecodeError) as err:
            raise ParsingError(
                f"Error while parsing functions definition:\n{err}"
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
            if len(function_dict.items()) > 4:
                errors.append("Too many entries in function")
            if len(errors):
                raise ParsingError(
                    "Missing or invalid fields in function:\n"
                    + ("\n".join(" - " + error for error in errors))
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
            except TypeError as err:
                raise ParsingError(f"Invalid parameter data: {err}")
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
                if len(prompt_dict.items()) != 1:
                    raise ParsingError("Too many entries in prompt")
                self.prompts.append(prompt)
        if len(self.prompts) and not len(self.functions):
            raise ParsingError(
                "Cannot compute prompts with an empty functions file"
            )
