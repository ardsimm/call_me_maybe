from enum import StrEnum
from pydantic import BaseModel, Field
from typing import List, Optional


class ParameterType(StrEnum):
    """The JSON-schema-style type names used in `functions_definition.json`."""

    INT = "int"
    FLOAT = "number"
    BOOL = "boolean"
    STRING = "string"


class Parameter(BaseModel):
    """A function parameter: its name, declared type, and generated value.

    Attributes
    ----------
    name : str
        The parameter's name.
    type : ParameterType
        The parameter's declared type.
    value : str or None
        The generated value, as the raw string produced by constrained
        decoding (parsed into its real Python type elsewhere); None before
        generation.

    Raises
    ------
    pydantic.ValidationError
        If `name` is empty or `type` is not a valid `ParameterType`.
    """

    name: str = Field(min_length=1)
    type: ParameterType = Field()
    value: Optional[str] = Field(default=None)


class Function(BaseModel):
    """A callable function's schema: its name, description, and parameters.

    Attributes
    ----------
    description : str
        The function's natural-language description.
    name : str
        The function's name.
    parameters : list of Parameter
        The function's parameters.

    Raises
    ------
    pydantic.ValidationError
        If `description` or `name` is empty.
    """

    description: str = Field(min_length=1)
    name: str = Field(min_length=1)
    parameters: List[Parameter] = Field()
