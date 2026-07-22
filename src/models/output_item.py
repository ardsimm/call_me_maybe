from typing import TypedDict, List
from .function import Argument


class OutputItem(TypedDict):
    prompt: str
    name: str
    arguments: List[Argument]
