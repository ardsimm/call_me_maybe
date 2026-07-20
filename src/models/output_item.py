from typing import TypedDict, List
from .arguments import Arguments


class OutputItem(TypedDict):
    prompt: str
    fn_name: str
    arguments: List[Arguments]
