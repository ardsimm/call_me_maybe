from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)
from src.adapter.adapter_factory import AdapterFactory
from src.adapter.adapter_type import AdapterType
from src.adapter.adapter_exceptions import DeserializationException


class Arguments(BaseModel):
    """CLI arguments, validated against the input files they name.

    Attributes
    ----------
    functions_definition : str
        Path to the functions-definition JSON file.
    input : str
        Path to the function-calling-tests JSON file (the prompts).
    output : str
        Path the output JSON array is written to.
    """

    model_config = ConfigDict(validate_assignment=True)
    functions_definition: str = Field(
        default="data/input/functions_definition.json"
    )
    input: str = Field(
        default="data/input/function_calling_tests.json"
    )
    output: str = Field(
        default="data/output/function_calling_results.json"
    )
