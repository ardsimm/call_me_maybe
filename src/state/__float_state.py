from functools import reduce
from typing import List
from src.model import Model
from .state import StateStage, State


class FloatStateStage(StateStage):
    INITIAL = (0,)
    PRE_FLOAT_POINT = (1,)
    FLOAT_POINT = (2,)
    POST_FLOAT_POINT = (3,)
    TERMINAL = 4


class FloatState(State):

    def __init__(self) -> None:
        super().__init__()
        self._stages = [
            FloatStateStage.INITIAL,
            FloatStateStage.PRE_FLOAT_POINT,
            FloatStateStage.FLOAT_POINT,
            FloatStateStage.POST_FLOAT_POINT,
            FloatStateStage.TERMINAL,
        ]

        digits_tokens: List[int] = reduce(
            lambda ac, el: ac + el, [
                self._tokenizer.encode(char).tolist()[0]
                for char in "0123456789"
            ], []
        )

        pre_float_point_tokens = []
        pre_float_point_tokens.extend(digits_tokens)
        pre_float_point_tokens.extend(self._tokenizer.encode(".").tolist()[0])

        post_float_point_tokens = []
        post_float_point_tokens.extend(digits_tokens)
        post_float_point_tokens.extend(Model.get_instance().string_end_sequences)

        self._stage_allowed_tokens = {
            FloatStateStage.INITIAL: digits_tokens,
            FloatStateStage.PRE_FLOAT_POINT: pre_float_point_tokens,
            FloatStateStage.FLOAT_POINT: digits_tokens,
            FloatStateStage.POST_FLOAT_POINT: post_float_point_tokens,
            FloatStateStage.TERMINAL: None,
        }

        self._stage_transition_tokens = {
            FloatStateStage.INITIAL: digits_tokens,
            FloatStateStage.PRE_FLOAT_POINT: self._tokenizer.encode(
                "."
            ).tolist()[0],
            FloatStateStage.FLOAT_POINT: digits_tokens,
            FloatStateStage.POST_FLOAT_POINT: Model.get_instance().string_end_sequences,
        }
