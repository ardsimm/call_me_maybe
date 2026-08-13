from typing import TypedDict, Union, Dict

ParameterDict = Dict[str, Union[int, float, str, bool]]

class OutputItem(TypedDict):
    prompt: str
    name: str
    parameters: ParameterDict
