from enum import Enum

from pydantic import BaseModel, Field, model_validator
from typing import List

class ArgumentType(Enum):
    INT = "int",
    FLOAT = "float",
    BOOL = "bool",
    STRING = "string"

class Argument(BaseModel):
    name: str = Field(min_length=1)
    type: ArgumentType = Field()

class Function(BaseModel):
    prompt: str = Field(min_length=1)
    name: str = Field(min_length=4)
    arguments: List[Argument] = Field()

    @model_validator(mode="after")
    def validate_model(self) -> "Function":
        if not self.name.startswith("fn_"):
            raise ValueError("Function name must begin with \"fn_\"")
        return self
