from functools import reduce
from typing import List
from src.model import Model
from .state import StateStage, State


class IntStateStage(StateStage):
    INITIAL = (0,)
    PRE_FLOAT_POINT = (1,)
    FLOAT_POINT = (2,)
    DATA = (3,)
    TERMINAL = 4


class IntState(State):

    def __init__(self) -> None:
        super().__init__()
        self._stages = [
            IntStateStage.INITIAL,
            IntStateStage.DATA,
            IntStateStage.TERMINAL,
        ]
        digits_tokens: List[int] = reduce(
            lambda ac, el: ac + el,
            [
                self._tokenizer.encode(char).tolist()[0]
                for char in "0123456789"
            ],
            [],
        )

        data_tokens = list(digits_tokens)
        data_tokens.extend(Model.get_instance().string_end_sequences)

        self._stage_allowed_tokens = {
            IntStateStage.INITIAL: digits_tokens,
            IntStateStage.DATA: data_tokens,
            IntStateStage.TERMINAL: None,
        }

        self._stage_transition_tokens = {
            IntStateStage.INITIAL: digits_tokens,
            IntStateStage.DATA: Model.get_instance().string_end_sequences,
        }
