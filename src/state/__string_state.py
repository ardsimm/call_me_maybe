from src.model.model import Model
from .state import StateStage, State


class StringStateStage(StateStage):
    """Stages of `StringState`."""

    INITIAL = (0,)
    DATA = (1,)
    TERMINAL = 2


class StringState(State):
    """`State` grammar for a JSON string: any tokens until an unescaped `"`.

    Unlike `IntState`/`FloatState`, this imposes no per-token constraint
    (INITIAL/DATA both allow any token); it only watches for a
    `Model.string_end_sequences` token to know when the value ends.
    """

    def __init__(self) -> None:
        """Build the allowed/transition token maps for string literals.

        Raises
        ------
        GenerationError
            Forwarded from `Model.string_end_sequences` if the vocab file
            cannot be loaded.
        """
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
