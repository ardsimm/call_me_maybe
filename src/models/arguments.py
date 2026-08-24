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
        min_length=6, default="data/input/functions_definition.json"
    )
    input: str = Field(
        min_length=6, default="data/input/function_calling_tests.json"
    )
    output: str = Field(
        min_length=6, default="data/output/function_calls.json"
    )

    @model_validator(mode="after")
    def validate_model(self) -> "Arguments":
        """Verify that `functions_definition` and `input` are valid JSON.

        Both files are opened and parsed through `JSONAdapter`, purely to
        fail fast on malformed JSON before the rest of the program starts;
        the parsed content itself is discarded here.

        `ParsingError` is imported locally (not at module level) to break
        a circular import: `src.parsing.__init__` imports `Parser`, which
        imports `Arguments` from this module, so importing
        `src.parsing.parser_exceptions` at module level here would force
        that cycle to run before `Arguments` finishes being defined.

        Returns
        -------
        Arguments
            `self`, unchanged.

        Raises
        ------
        OSError
            If `functions_definition` or `input` cannot be opened.
        ParsingError
            If either file's content is not valid JSON.
        """
        from src.parsing.parser_exceptions import ParsingError

        json_adapter = AdapterFactory.get_instance(AdapterType.JSON)

        with (
            open(self.functions_definition) as functions_definitions,
            open(self.input) as input_file,
        ):
            try:
                json_adapter.parse(functions_definitions.read())
            except DeserializationException as e:
                raise ParsingError(
                    f"Invalid json format for file {self.input}: {e}"
                )
            try:
                json_adapter.parse(input_file.read())
            except DeserializationException as e:
                raise ParsingError(
                    f"Invalid json format for file {self.input}: {e}"
                )
        return self
