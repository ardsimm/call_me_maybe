from typing import TypedDict, Union, Dict

ParameterDict = Dict[str, Union[int, float, str, bool]]


class OutputItem(TypedDict):
    """One result row written to the output JSON file.

    Attributes
    ----------
    prompt : str
        The original natural-language request.
    name : str
        The name of the function chosen for `prompt`.
    parameters : ParameterDict
        The generated arguments, keyed by parameter name.
    """

    prompt: str
    name: str
    parameters: ParameterDict
