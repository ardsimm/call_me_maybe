from pydantic import BaseModel, Field, model_validator, ValidationError
import json


class Arguments(BaseModel):
    functions_definition: str = Field(
        min_length=6, default="functions_definition.json"
    )
    input: str = Field(
        min_length=6, default="function_calling_tests.json"
    )
    output: str = Field(min_length=6, default="function_calls.json")
    model: str = Field(min_length=3, default="Qwen/Qwen3-0.6B")


    @model_validator(mode="after")
    def validate_model(self) -> "Arguments":
        try:
            json.loads(self.functions_definition)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid json format for file {self.functions_definition}: {e}")
        try:
            json.loads(self.input)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid json format for file {self.input}: {e}")
        return self
