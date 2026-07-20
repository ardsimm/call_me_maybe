from enum import Enum
from pydantic import BaseModel, Field
from typing import List


class ArgumentType(Enum):
    INT = ("int",)
    FLOAT = ("float",)
    BOOL = ("bool",)
    STRING = "string"


class Argument(BaseModel):
    name: str = Field(min_length=1)
    type: ArgumentType = Field()


class Function(BaseModel):
    description: str = Field(min_length=1)
    name: str = Field(min_length=1)
    arguments: List[Argument] = Field()
