from abc import ABC, abstractmethod
from typing import Any


class Parser(ABC):

    @abstractmethod
    def parse(self, source: Any) -> Any:
        pass
