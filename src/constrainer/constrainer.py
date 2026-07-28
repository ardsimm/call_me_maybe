from abc import ABC, abstractmethod
from typing import List
from src.state.state import State


class Constrainer(ABC):

    __state: State

    def __init__(self, state: State) -> None:
        self.__state = state

    @property
    def state(self) -> State:
        return self.__state

    @abstractmethod
    def constrain_tokens(
        self,
        tokens: List[int],
    ) -> List[int]:
        pass

    @abstractmethod
    def pick_token(
        self,
        logits: List[float]
    ) -> int:
        pass
