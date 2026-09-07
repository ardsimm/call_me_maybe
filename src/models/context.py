from enum import StrEnum
from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class ParameterType(StrEnum):
    """The JSON-schema-style type names used in `functions_definition.json`."""

    INT = "int"
    FLOAT = "number"
    BOOL = "boolean"
    STRING = "string"


class Parameter(BaseModel):
    """One parameter entry of `functions_definition.json`, plus its value.

    In the input file a parameter is only `{"type": ...}`, keyed by its
    name inside its function's `parameters` object -- so `name` is not
    present in the JSON and is filled in from that key afterwards by
    `CallMeMaybe.__get_context`, while `value` is filled in later still
    by the generator.

    Attributes
    ----------
    type : ParameterType
        The parameter's declared type, as written in the input file.
    name : str
        The parameter's name, defaulting to `"[None]"` until the key it
        was declared under is copied into it.
    value : str or None
        The generated value, as the raw string produced by constrained
        decoding (parsed into its real Python type elsewhere); None
        before generation.

    Raises
    ------
    pydantic.ValidationError
        If `type` is missing or is not one of `ParameterType`'s values,
        or if the entry carries any key besides `type`/`name`/`value`
        (`extra="forbid"`).
    """

    model_config = ConfigDict(extra="forbid")
    type: ParameterType = Field()
    name: str = Field(default="[None]")
    value: Optional[str] = Field(default=None)


class Returns(BaseModel):
    """The `returns` entry of one function in `functions_definition.json`.

    Only parsed so the key is accepted by validation; the return type is
    never used for generation, since only parameters are generated.

    Attributes
    ----------
    type : ParameterType
        The function's declared return type.

    Raises
    ------
    pydantic.ValidationError
        If `type` is missing, is not one of `ParameterType`'s values, or
        the entry carries any other key (`extra="forbid"`).
    """

    model_config = ConfigDict(extra="forbid")
    type: ParameterType = Field()


class Function(BaseModel):
    """One function entry of `functions_definition.json`.

    Attributes
    ----------
    name : str
        The function's name -- one of the candidates the name trie is
        built from.
    description : str
        The function's natural-language description, shown to the model
        as part of the name-selection prompt.
    parameters : dict of str to Parameter
        The function's parameters, keyed by name and kept in the input
        file's declaration order, which is also the order they are
        generated in.
    returns : Returns
        The function's declared return type (unused for generation).

    Raises
    ------
    pydantic.ValidationError
        If any of the four keys is missing or has the wrong type, or if
        the entry carries an extra key (`extra="forbid"`).
    """

    model_config = ConfigDict(extra="forbid")
    name: str = Field()
    description: str = Field()
    parameters: Dict[str, Parameter] = Field()
    returns: Returns = Field()


class PromptEntry(BaseModel):
    """One entry of the prompts file: a single `{"prompt": ...}` object.

    Attributes
    ----------
    prompt : str
        The user's natural-language request.

    Raises
    ------
    pydantic.ValidationError
        If `prompt` is missing, is not a string, or the entry carries any
        other key (`extra="forbid"`).
    """

    model_config = ConfigDict(extra="forbid")
    prompt: str = Field()


class Context(BaseModel):
    """The loaded, validated set of functions and prompts for a run.

    Purely declarative: validation of both input files is done by
    pydantic itself, through `Context.model_validate` in
    `CallMeMaybe.__get_context`, rather than by hand-written checks here.
    `extra="forbid"` on every model in this module is what turns an
    unexpected key anywhere in either file into a validation error.

    Attributes
    ----------
    functions : list of Function
        The functions parsed from `arguments.functions_definition`.
    prompts : list of PromptEntry
        The prompts parsed from `arguments.input`.

    Raises
    ------
    pydantic.ValidationError
        From `model_validate`, if either file's content does not match
        the shape described by the models above.
    """

    model_config = ConfigDict(extra="forbid")
    functions: List[Function] = Field()
    prompts: List[PromptEntry] = Field()
