from typing import List, Optional

from src.state.state import State
from . import Constrainer


class BooleanConstrainer(Constrainer):
    # TODO: Implement Trie
    def __init__(self, state: State) -> None:
        super().__init__(state)
        raise NotImplementedError(
            f"Class {self.__class__.__name__}"
            + "not implemented"
        )

    def constrain_logits(
        self,
        logits: List[float],
    ) -> List[float]:
        raise NotImplementedError(
            "Method constraint_logits"
            + f" of class {self.__class__.__name__}"
            + "not implemented"
        )

    def pick_token(
        self,
        logits: List[float]
    ) -> Optional[int]:
        raise NotImplementedError(
            "Method pick_token"
            + f" of class {self.__class__.__name__}"
            + "not implemented"
        )
