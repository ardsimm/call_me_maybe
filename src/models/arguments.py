from pydantic import BaseModel, Field, model_validator
import json


class Arguments(BaseModel):
    functions_definitions: str = Field(
        min_length=6, default="data/input/functions_definitions.json"
    )
    input: str = Field(
        min_length=6, default="data/input/function_calling_tests.json"
    )
    output: str = Field(min_length=6, default="function_calls.json")
    model: str = Field(min_length=3, default="Qwen/Qwen3-0.6B")


    @model_validator(mode="after")
    def validate_model(self) -> "Arguments":
        with (
            open(self.functions_definitions) as functions_definitions,
            open(self.input) as input_file
        ):
            try:
                json.loads(functions_definitions.read())
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid json format for file {self.input}: {e}")
            try:
                json.loads(input_file.read())
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid json format for file {self.input}: {e}")
        return self
