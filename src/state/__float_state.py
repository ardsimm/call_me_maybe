from functools import reduce
from typing import List
from src.model import Model
from .state import StateStage, State


class FloatStateStage(StateStage):
    INITIAL = 0
    PRE_FLOAT_POINT = 1
    FLOAT_POINT = 2
    POST_FLOAT_POINT = 3
    POST_SCIENTIFIC_E_TOKEN = 4
    POST_SCIENTIFIC_SIGN = 5
    POST_SCIENTIFIC_EXP = 6
    TERMINAL = 7


class FloatState(State):

    minus_token: List[int]
    plus_token: List[int]
    dot_token: List[int]
    lower_e_token: List[int]
    upper_e_token: List[int]
    string_end_sequences: List[int]

    def __init__(self) -> None:
        super().__init__()
        self._stages = [
            FloatStateStage.INITIAL,
            FloatStateStage.PRE_FLOAT_POINT,
            FloatStateStage.FLOAT_POINT,
            FloatStateStage.POST_FLOAT_POINT,
            FloatStateStage.POST_SCIENTIFIC_E_TOKEN,
            FloatStateStage.POST_SCIENTIFIC_SIGN,
            FloatStateStage.POST_SCIENTIFIC_EXP,
            FloatStateStage.TERMINAL,
        ]

        self.minus_token = self._tokenizer.encode("-").tolist()[0]
        self.plus_token = self._tokenizer.encode("+").tolist()[0]
        self.dot_token = self._tokenizer.encode(".").tolist()[0]
        self.lower_e_token = self._tokenizer.encode("e").tolist()[0]
        self.upper_e_token = self._tokenizer.encode("E").tolist()[0]
        self.string_end_sequences = Model.get_instance().string_end_sequences
        self.digits_tokens: List[int] = reduce(
            lambda ac, el: ac + el,
            [
                self._tokenizer.encode(char).tolist()[0]
                for char in "0123456789"
            ],
            [],
        )

        self._stage_allowed_tokens = {
            FloatStateStage.INITIAL: self.minus_token + self.digits_tokens,
            FloatStateStage.PRE_FLOAT_POINT: (
                self.digits_tokens + self.dot_token
            ),
            FloatStateStage.FLOAT_POINT: self.digits_tokens,
            FloatStateStage.POST_FLOAT_POINT: (
                self.digits_tokens
                + self.string_end_sequences
                + self.lower_e_token
                + self.upper_e_token
            ),
            FloatStateStage.POST_SCIENTIFIC_E_TOKEN: (
                self.plus_token + self.minus_token
            ),
            FloatStateStage.POST_SCIENTIFIC_SIGN: self.digits_tokens,
            FloatStateStage.POST_SCIENTIFIC_EXP: (
                self.digits_tokens + self.string_end_sequences
            ),
            FloatStateStage.TERMINAL: None,
        }

        self._stage_transition_tokens = {
            FloatStateStage.INITIAL: self.minus_token + self.digits_tokens,
            FloatStateStage.PRE_FLOAT_POINT: self.dot_token,
            FloatStateStage.FLOAT_POINT: self.digits_tokens,
            FloatStateStage.POST_FLOAT_POINT: (
                self.string_end_sequences
                + self.lower_e_token
                + self.upper_e_token
            ),
            FloatStateStage.POST_SCIENTIFIC_E_TOKEN: (
                self.minus_token + self.plus_token
            ),
            FloatStateStage.POST_SCIENTIFIC_SIGN: (self.digits_tokens),
            FloatStateStage.POST_SCIENTIFIC_EXP: (self.string_end_sequences),
        }

    def _advance_stage(self, token: int) -> None:
        if self.current_stage not in [FloatStateStage.POST_FLOAT_POINT]:
            super()._advance_stage(token)
        else:
            if (
                token
                in self.lower_e_token + self.upper_e_token
            ):
                self.current_stage = FloatStateStage.POST_SCIENTIFIC_E_TOKEN
            elif token in self.string_end_sequences:
                self.current_stage = FloatStateStage.TERMINAL
