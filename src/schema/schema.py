from abc import ABC, abstractmethod
from typing import Any
from ..adapter import Adapter


class Schema(ABC):

    __adpater: Adapter

    @abstractmethod
    def init_schema(self) -> Any:
        pass

    @abstractmethod
    def get_schema(self) -> Any:
        pass
