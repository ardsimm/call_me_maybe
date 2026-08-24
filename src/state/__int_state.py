from functools import reduce
from typing import List
from src.model import Model
from .state import StateStage, State


class IntStateStage(StateStage):
    """Stages of integer generation.

    `INITIAL` is the first token (a digit or a leading `-`); a `-` there
    routes to `POST_MINUS` (which forces a digit next, so a bare `-` can
    never terminate the number), while a digit routes straight to
    `POST_DIGIT`. `POST_DIGIT` accepts more digits or a
    `string_end_sequences` token, which ends generation at `TERMINAL`.
    """

    INITIAL = 0
    POST_MINUS = 1
    POST_DIGIT = 2
    TERMINAL = 3


class IntState(State):
    """`State` accepting a JSON integer, e.g. `-42`.

    `_advance_stage` is overridden because `INITIAL` branches to two
    different next stages depending on whether the first token is `-`
    (to `POST_MINUS`) or a digit (straight to `POST_DIGIT`) -- the base
    class's linear `_stages` list can only express a single next stage
    per transition.
    """

    minus_token: List[int]

    def __init__(self) -> None:
        """Build the digit/minus token sets and the stage transition maps."""
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
        """Advance past `INITIAL` by branching on whether `token` is `-`.

        Every other stage falls back to the base class's linear
        transition logic.

        Parameters
        ----------
        token : int
            The token id that was just emitted.
        """
        if self.current_stage != IntStateStage.INITIAL:
            super()._advance_stage(token)
        else:
            if token in self.minus_token:
                self.current_stage = IntStateStage.POST_MINUS
            else:
                self.current_stage = IntStateStage.POST_DIGIT
