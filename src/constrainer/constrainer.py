from abc import ABC, abstractmethod
from typing import List, Optional
from src.state.state import State


class Constrainer(ABC):
    """Picks the next token from raw logits under a `State`'s grammar."""

    __state: State

    def __init__(self, state: State) -> None:
        """Store the `State` driving this constrainer's token selection.

        Parameters
        ----------
        state : State
            The state machine to consult and advance on each pick.
        """
        self.__state = state

    @property
    def state(self) -> State:
        """State : The state machine driving this constrainer."""
        return self.__state

    @abstractmethod
    def pick_token(
        self,
        logits: List[float],
    ) -> Optional[int]:
        """Pick the highest-scoring token allowed by `state`, advancing it.

        Parameters
        ----------
        logits : list of float
            Raw per-token logits for the next generation step.

        Returns
        -------
        int or None
            The picked token id, or None if `state` signals generation is
            complete.
        """
        pass
