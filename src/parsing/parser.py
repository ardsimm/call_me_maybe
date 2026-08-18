from abc import ABC, abstractmethod
from typing import Any
from src.models.arguments import Arguments


class Parser(ABC):

    @abstractmethod
    def parse(self, source: Any) -> Arguments:
        pass
