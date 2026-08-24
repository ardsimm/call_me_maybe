from functools import reduce
from typing import List
from src.model import Model
from .state import StateStage, State


class FloatStateStage(StateStage):
    """Stages of float generation, including scientific notation.

    `INITIAL` branches on the first token: `-` routes to
    `POST_MINUS_TOKEN` (forcing a digit next, so a bare `-` can never
    terminate the number), a digit routes straight to `PRE_FLOAT_POINT`.
    `PRE_FLOAT_POINT` accepts more digits or the decimal point
    (`FLOAT_POINT`), which forces a digit (`POST_FLOAT_POINT`).
    `POST_FLOAT_POINT` branches again: more digits, a
    `string_end_sequences` token (ending generation at `TERMINAL`), or
    `e`/`E` starting scientific notation (`POST_SCIENTIFIC_E_TOKEN`),
    which forces a `+`/`-` sign (`POST_SCIENTIFIC_SIGN`), then digits
    (`POST_SCIENTIFIC_EXP`), then a `string_end_sequences` token.
    """

    INITIAL = 0
    POST_MINUS_TOKEN = 1
    PRE_FLOAT_POINT = 2
    FLOAT_POINT = 3
    POST_FLOAT_POINT = 4
    POST_SCIENTIFIC_E_TOKEN = 5
    POST_SCIENTIFIC_SIGN = 6
    POST_SCIENTIFIC_EXP = 7
    TERMINAL = 8


class FloatState(State):
    """`State` accepting a JSON float, e.g. `-6.022e+23`.

    `_advance_stage` is overridden because both `INITIAL` and
    `POST_FLOAT_POINT` branch to more than one possible next stage
    depending on the emitted token -- the base class's linear `_stages`
    list can only express a single next stage per transition.
    """

    minus_token: List[int]
    plus_token: List[int]
    dot_token: List[int]
    lower_e_token: List[int]
    upper_e_token: List[int]
    string_end_sequences: List[int]

    def __init__(self) -> None:
        """Build the digit/sign/point/exponent token sets and stage maps."""
        super().__init__()
        self._stages = [
            FloatStateStage.INITIAL,
            FloatStateStage.POST_MINUS_TOKEN,
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
            FloatStateStage.POST_MINUS_TOKEN: self.digits_tokens,
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
            FloatStateStage.POST_MINUS_TOKEN: self.digits_tokens,
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
        """Advance past `INITIAL`/`POST_FLOAT_POINT` by branching on `token`.

        Every other stage falls back to the base class's linear
        transition logic.

        Parameters
        ----------
        token : int
            The token id that was just emitted.
        """
        if self.current_stage not in [
            FloatStateStage.INITIAL,
            FloatStateStage.POST_FLOAT_POINT
        ]:
            super()._advance_stage(token)
        elif self.current_stage == FloatStateStage.INITIAL:
            if token in self.minus_token:
                self.current_stage = FloatStateStage.POST_MINUS_TOKEN
            else:
                self.current_stage = FloatStateStage.PRE_FLOAT_POINT
        else:
            if (
                token
                in self.lower_e_token + self.upper_e_token
            ):
                self.current_stage = FloatStateStage.POST_SCIENTIFIC_E_TOKEN
            elif token in self.string_end_sequences:
                self.current_stage = FloatStateStage.TERMINAL
