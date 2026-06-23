from typing import Optional
from pydantic import BaseModel, Field


class Argument(BaseModel):
    functions_definition: Optional[str] = Field(
        min_length=6, default="functions_definition.json"
    )
    input: Optional[str] = Field(
        min_length=6, default="function_calling_tests.json"
    )
    output: Optional[str] = Field(min_length=6, default="function_calls.json")
    model: Optional[str] = Field(min_length=3, default="Qwen/Qwen3-0.6B")
