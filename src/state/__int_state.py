from functools import reduce
from typing import List
from src.model import Model
from .state import StateStage, State


class IntStateStage(StateStage):
    INITIAL = 0
    POST_MINUS = 1
    POST_DIGIT = 2
    TERMINAL = 3


class IntState(State):

    minus_token: List[int]

    def __init__(self) -> None:
        super().__init__()
        self._stages = [
            IntStateStage.INITIAL,
            IntStateStage.POST_MINUS,
            IntStateStage.POST_DIGIT,
            IntStateStage.TERMINAL,
        ]

        self.minus_token = self._tokenizer.encode("-").tolist()[0]

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
            IntStateStage.INITIAL: self.minus_token + digits_tokens,
            IntStateStage.POST_MINUS: digits_tokens,
            IntStateStage.POST_DIGIT: (
                digits_tokens + string_end_sequences
            ),
            IntStateStage.TERMINAL: None,
        }

        self._stage_transition_tokens = {
            IntStateStage.INITIAL: digits_tokens + self.minus_token,
            IntStateStage.POST_MINUS: digits_tokens,
            IntStateStage.POST_DIGIT: string_end_sequences,
        }

    def _advance_stage(self, token: int) -> None:
        if self.current_stage != IntStateStage.INITIAL:
            super()._advance_stage(token)
        else:
            if token in self.minus_token:
                self.current_stage = IntStateStage.POST_MINUS
            else:
                self.current_stage = IntStateStage.POST_DIGIT
