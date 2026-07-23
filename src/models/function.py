from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional


class ParameterType(Enum):
    INT = ("int",)
    FLOAT = ("float",)
    BOOL = ("bool",)
    STRING = "string"


class Parameter(BaseModel):
    name: str = Field(min_length=1)
    type: ParameterType = Field()
    value: Optional[str] = None


class Function(BaseModel):
    description: str = Field(min_length=1)
    name: str = Field(min_length=1)
    parameters: List[Parameter] = Field()
