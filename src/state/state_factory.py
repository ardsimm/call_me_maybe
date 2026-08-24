from typing import List

from src.state.trie_state import TrieState

from .__float_state import FloatState
from .__int_state import IntState
from .__string_state import StringState
from .state import State
from .state_type import StateType


class StateFactory:

    @staticmethod
    def get_instance(type: StateType) -> State:
        if type == StateType.STRING_STATE:
            return StringState()
        if type == StateType.INT_STATE:
            return IntState()
        if type == StateType.FLOAT_STATE:
            return FloatState()
        raise ValueError(f"Invalid state type {type}")

    @staticmethod
    def get_trie_state_instance(words: List[List[int]]) -> TrieState:
        state = TrieState()
        state.init_trie_state(words)
        return state
