from pydantic import BaseModel, Field


class Arguments(BaseModel):
    functions_definition: str = Field(
        min_length=6, default="functions_definition.json"
    )
    input: str = Field(
        min_length=6, default="function_calling_tests.json"
    )
    output: str = Field(min_length=6, default="function_calls.json")
    model: str = Field(min_length=3, default="Qwen/Qwen3-0.6B")
