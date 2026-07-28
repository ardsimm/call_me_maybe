from src.state.state import StateStage
from . import State


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
            IntStateStage.INITIAL: digits_tokens,
            IntStateStage.DATA: digits_tokens.extend(
                self._tokenizer.encode('"').tolist()[0]
            ),
            IntStateStage.TERMINAL: None,
        }

        self._stage_transition_tokens = {
            IntStateStage.INITIAL: digits_tokens,
            IntStateStage.DATA: self._tokenizer.encode('"').tolist()[0],
        }
