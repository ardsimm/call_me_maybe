from src.state.state import StateStage
from . import State


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
        digits_tokens = (
            self._tokenizer.encode("0")
            .tolist()[0]
            .extend(self._tokenizer.encode("1").tolist()[0])
            .extend(self._tokenizer.encode("2").tolist()[0])
            .extend(self._tokenizer.encode("3").tolist()[0])
            .extend(self._tokenizer.encode("4").tolist()[0])
            .extend(self._tokenizer.encode("5").tolist()[0])
            .extend(self._tokenizer.encode("6").tolist()[0])
            .extend(self._tokenizer.encode("7").tolist()[0])
            .extend(self._tokenizer.encode("8").tolist()[0])
            .extend(self._tokenizer.encode("9").tolist()[0])
        )

        self._stage_allowed_tokens = {
            FloatStateStage.INITIAL: digits_tokens,
            FloatStateStage.PRE_FLOAT_POINT: digits_tokens.extend(
                self._tokenizer.encode(".").tolist()[0]
            ),
            FloatStateStage.FLOAT_POINT: digits_tokens,
            FloatStateStage.POST_FLOAT_POINT: digits_tokens.extend(
                self._tokenizer.encode('"').tolist()[0]
            ),
            FloatStateStage.TERMINAL: None,
        }

        self._stage_transition_tokens = {
            FloatStateStage.INITIAL: digits_tokens,
            FloatStateStage.PRE_FLOAT_POINT: self._tokenizer.encode(
                "."
            ).tolist()[0],
            FloatStateStage.FLOAT_POINT: self._tokenizer.encode(
                digits_tokens
            ).tolist()[0],
            FloatStateStage.POST_FLOAT_POINT: self._tokenizer.encode(
                '"'
            ).tolist()[0],
        }
