from src.state.state import State
from . import Constrainer


class FunctionNameConstrainer(Constrainer):
    # TODO: Implement Trie
    def __init__(self, state: State) -> None:
        super().__init__(state)
        raise NotImplementedError(
            f"Class {self.__class__.__name__}"
            + "not implemented"
        )
