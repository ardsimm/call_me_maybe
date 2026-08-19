from abc import ABC, abstractmethod
from typing import List, Optional
from src.state.state import State


class Constrainer(ABC):

    __state: State

    def __init__(self, state: State) -> None:
        self.__state = state

    @property
    def state(self) -> State:
        return self.__state

    @abstractmethod
    def pick_token(
        self,
        logits: List[float],
    ) -> Optional[int]:
        pass
