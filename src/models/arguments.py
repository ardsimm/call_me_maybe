from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)
import json
from src.adapter.adapter_factory import AdapterFactory
from src.adapter.adapter_type import AdapterType


class Arguments(BaseModel):

    model_config = ConfigDict(validate_assignment=True)
    functions_definition: str = Field(
        min_length=6, default="data/input/functions_definition.json"
    )
    input: str = Field(
        min_length=6, default="data/input/function_calling_tests.json"
    )
    output: str = Field(min_length=6, default="function_calls.json")
    model: str = Field(min_length=3, default="Qwen/Qwen3-0.6B")

    @model_validator(mode="after")
    def validate_model(self) -> "Arguments":
        json_adapter = AdapterFactory.get_instance(AdapterType.JSON)

        with (
            open(self.functions_definition) as functions_definitions,
            open(self.input) as input_file,
        ):
            try:
                json_adapter.parse(functions_definitions.read())
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid json format for file {self.input}: {e}"
                )
            try:
                json_adapter.parse(input_file.read())
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid json format for file {self.input}: {e}"
                )
        return self
