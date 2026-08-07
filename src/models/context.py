from typing import List, Dict, TypedDict
from src.models.arguments import Arguments
from src.models.function import Function, Parameter, ParameterType
from pydantic import BaseModel, Field
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
            function = Function(
                name=function_dict["name"],
                description=function_dict["description"],
                parameters=[
                    Parameter(name=key, type=ParameterType(value["type"]))
                    for key, value in function_dict["parameters"].items()
                ],
            )
            self.functions.append(function)
        with open(arguments.input) as prompts:
            prompts_dicts = json.loads(prompts.read())
            for prompt_dict in prompts_dicts:
                self.prompts.append(prompt_dict["prompt"])
