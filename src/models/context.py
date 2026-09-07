from enum import StrEnum
from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class ParameterType(StrEnum):
    """The JSON-schema-style type names used in `functions_definition.json`."""

    INT = "int"
    FLOAT = "number"
    BOOL = "boolean"
    STRING = "string"


class Parameter(BaseModel):
    """Raw shape of one parameter entry in `functions_definition.json`."""

    model_config = ConfigDict(extra="forbid")
    type: ParameterType = Field()
    name: str = Field(default="[None]")
    value: Optional[str] = Field(default=None)


class Returns(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: ParameterType = Field()


class Function(BaseModel):
    """Raw shape of one function entry in `functions_definition.json`."""

    model_config = ConfigDict(extra="forbid")
    name: str = Field()
    description: str = Field()
    parameters: Dict[str, Parameter] = Field()
    returns: Returns = Field()


class PromptEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field()


class Functions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    functions: List[Function]


class Prompts(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompts: List[PromptEntry]


class Context(BaseModel):
    """The loaded, validated set of functions and prompts for a run.

    Attributes
    ----------
    functions : list of Function
        The functions parsed from `arguments.functions_definition`.
    prompts : list of str
        The prompts parsed from `arguments.input`.
    """

    model_config = ConfigDict(extra="forbid")
    functions: List[Function] = Field()
    prompts: List[PromptEntry] = Field()
