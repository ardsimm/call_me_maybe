from src.state.state import StateStage
from . import State


class StringStateStage(StateStage):
    INITIAL = (0,)
    DATA = (1,)
    TERMINAL = 2


class StringState(State):

    def __init__(self) -> None:
        super().__init__()
        self._stages = [
            StringStateStage.INITIAL,
            StringStateStage.DATA,
            StringStateStage.TERMINAL,
        ]
        self._stage_allowed_tokens = {
            StringStateStage.INITIAL: [],
            StringStateStage.DATA: [],
            StringStateStage.TERMINAL: None,
        }
        self._stage_transition_tokens = {
            StringStateStage.INITIAL: [],
            StringStateStage.DATA: self._tokenizer.encode('"').tolist()[0],
        }
