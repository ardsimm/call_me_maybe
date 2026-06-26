from abc import ABC, abstractmethod
from ..state import State
from typing import Any


class Tokenizer(ABC):

    __state: State

    @abstractmethod
    def encode(self, data: Any) -> Any:
        pass

    @abstractmethod
    def decode(data: Any) -> Any:
        pass
