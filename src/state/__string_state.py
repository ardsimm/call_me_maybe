from src.model.model import Model
from .state import StateStage, State


class StringStateStage(StateStage):
    INITIAL = 0,
    DATA = 1,
    TERMINAL = 2


class StringState(State):

    def __init__(self) -> None:
        super().__init__()
        model = Model.get_instance()
        string_end_sequences = model.string_end_sequences

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
            StringStateStage.DATA: string_end_sequences,
        }
