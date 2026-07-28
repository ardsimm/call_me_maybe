from typing import List

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
        initial_tokens: List[int] = self._tokenizer.encode("0").tolist()[0]
        initial_tokens.extend(self._tokenizer.encode("1").tolist()[0])
        initial_tokens.extend(self._tokenizer.encode("2").tolist()[0])
        initial_tokens.extend(self._tokenizer.encode("3").tolist()[0])
        initial_tokens.extend(self._tokenizer.encode("4").tolist()[0])
        initial_tokens.extend(self._tokenizer.encode("5").tolist()[0])
        initial_tokens.extend(self._tokenizer.encode("6").tolist()[0])
        initial_tokens.extend(self._tokenizer.encode("7").tolist()[0])
        initial_tokens.extend(self._tokenizer.encode("8").tolist()[0])
        initial_tokens.extend(self._tokenizer.encode("9").tolist()[0])

        pre_float_point_tokens = []
        pre_float_point_tokens.extend(initial_tokens)
        pre_float_point_tokens.extend(self._tokenizer.encode(".").tolist()[0])

        post_float_point_tokens = []
        post_float_point_tokens.extend(initial_tokens)
        post_float_point_tokens.extend(self._tokenizer.encode('"').tolist()[0])

        self._stage_allowed_tokens = {
            FloatStateStage.INITIAL: initial_tokens,
            FloatStateStage.PRE_FLOAT_POINT: pre_float_point_tokens,
            FloatStateStage.FLOAT_POINT: initial_tokens,
            FloatStateStage.POST_FLOAT_POINT: post_float_point_tokens,
            FloatStateStage.TERMINAL: None,
        }

        self._stage_transition_tokens = {
            FloatStateStage.INITIAL: initial_tokens,
            FloatStateStage.PRE_FLOAT_POINT: self._tokenizer.encode(
                "."
            ).tolist()[0],
            FloatStateStage.FLOAT_POINT: initial_tokens,
            FloatStateStage.POST_FLOAT_POINT: self._tokenizer.encode(
                '"'
            ).tolist()[0],
        }
