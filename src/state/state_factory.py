from typing import List

from src.state.__trie_state import TrieState

from .__float_state import FloatState
from .__int_state import IntState
from .__string_state import StringState
from .state import State
from .state_type import StateType


class StateFactory:
    """Builds `State` instances for a given `StateType` or a trie of words."""

    @staticmethod
    def get_instance(type: StateType) -> State:
        """Build a new `State` for `type`.

        Parameters
        ----------
        type : StateType
            Which state implementation to build.

        Returns
        -------
        State
            A new state instance for `type`.

        Raises
        ------
        ValueError
            If `type` is none of `StateType.STRING_STATE`, `INT_STATE`, or
            `FLOAT_STATE`. There is no `StateType` member for `TrieState`;
            use `get_trie_state_instance` to build one instead.
        """
        if type == StateType.STRING_STATE:
            return StringState()
        if type == StateType.INT_STATE:
            return IntState()
        if type == StateType.FLOAT_STATE:
            return FloatState()
        raise ValueError(f"Invalid state type {type}")

    @staticmethod
    def get_trie_state_instance(words: List[List[int]]) -> TrieState:
        """Build a new `TrieState` initialized with `words`.

        Parameters
        ----------
        words : list of list of int
            The token-id sequences accepted by the resulting trie.

        Returns
        -------
        TrieState
            A new trie state accepting exactly `words` (each terminated by
            any of `Model.string_end_sequences`).

        Raises
        ------
        GenerationError
            Forwarded from `Model.string_end_sequences` if the vocab file
            cannot be loaded or parsed.
        """
        state = TrieState()
        state.init_trie_state(words)
        return state
