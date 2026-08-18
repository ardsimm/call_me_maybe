from enum import StrEnum
from pydantic import BaseModel, Field
from typing import List, Optional


class ParameterType(StrEnum):
    INT = "int"
    FLOAT = "number"
    BOOL = "boolean"
    STRING = "string"


class Parameter(BaseModel):
    name: str = Field(min_length=1)
    type: ParameterType = Field()
    value: Optional[str] = Field(default=None)


class Function(BaseModel):
    description: str = Field(min_length=1)
    name: str = Field(min_length=1)
    parameters: List[Parameter] = Field()
