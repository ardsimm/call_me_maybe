from typing import TypedDict, List
from .function import Parameter


class OutputItem(TypedDict):
    prompt: str
    name: str
    arguments: List[Parameter]
