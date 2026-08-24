from enum import Enum


class StateType(Enum):
    """The non-trie `State` implementations `StateFactory` can build."""

    FLOAT_STATE = 0
    INT_STATE = 1
    STRING_STATE = 2
