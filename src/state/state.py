from abc import ABC, abstractmethod
from typing import Any


class State(ABC):

    @abstractmethod
    def get_current_state(self) -> Any:
        pass

    @abstractmethod
    def set_current_state(self) -> None:
        pass
