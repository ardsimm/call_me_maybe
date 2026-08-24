from functools import reduce
from typing import List
from src.model import Model
from .state import StateStage, State


class IntStateStage(StateStage):
    INITIAL = 0
    DATA = 1
    TERMINAL = 2


class IntState(State):

    def __init__(self) -> None:
        super().__init__()
        self._stages = [
            IntStateStage.INITIAL,
            IntStateStage.DATA,
            IntStateStage.TERMINAL,
        ]

        minus_token = self._tokenizer.encode("-").tolist()[0]

        digits_tokens: List[int] = reduce(
            lambda ac, el: ac + el,
            [
                self._tokenizer.encode(char).tolist()[0]
                for char in "0123456789"
            ],
            [],
        )

        string_end_sequences = Model.get_instance().string_end_sequences

        self._stage_allowed_tokens = {
            IntStateStage.INITIAL: minus_token + digits_tokens,
            IntStateStage.DATA: (
                digits_tokens + string_end_sequences
            ),
            IntStateStage.TERMINAL: None,
        }

        self._stage_transition_tokens = {
            IntStateStage.INITIAL: digits_tokens,
            IntStateStage.DATA: string_end_sequences,
        }
