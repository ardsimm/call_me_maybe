from enum import Enum
from typing import Dict, List, Optional
from src.tokenize.tokenizer import Tokenizer
from src.tokenize.tokenizer_factory import TokenizerFactory
from src.tokenize.tokenizer_type import TokenizerType


class StateStage(Enum):
    """Base class for a `State`'s ordered stage enum.

    Concrete states define their own `StateStage` subclass listing the
    stages generation can be in (e.g. before/after a decimal point).
    """

    pass


class State:
    """Finite-state-machine base class driving constrained decoding.

    A `State` holds an ordered list of `_stages`, and per-stage maps of
    which tokens may legally be emitted (`_stage_allowed_tokens`) and
    which emitted tokens advance to the next stage
    (`_stage_transition_tokens`). `Constrainer` reads
    `get_allowed_tokens()` to mask logits, then calls `update_last_token`
    to drive the stage forward. Subclasses populate `_stages`,
    `_stage_allowed_tokens`, and `_stage_transition_tokens` in their own
    `__init__` and may override `_advance_stage` for non-linear stage
    transitions (e.g. branching to different stages depending on the
    emitted token).
    """

    _stages: List[StateStage]
    _tokenizer: Tokenizer
    _stage_allowed_tokens: Dict[StateStage, Optional[List[int]]]
    _stage_transition_tokens: Dict[StateStage, List[int]]
    __current_stage_idx: int

    def __init__(self) -> None:
        """Fetch the default `Tokenizer` and start at the first stage."""
        self._tokenizer = TokenizerFactory.get_instance(TokenizerType.DEFAULT)
        self.__current_stage_idx = 0

    def _advance_stage(self, token: int) -> None:
        """Move to the next stage if `token` is a transition token.

        The current stage advances when `token` is one of its
        `_stage_transition_tokens`, or when that stage has no transition
        tokens at all (an empty list means "any token ends this stage").

        Parameters
        ----------
        token : int
            The token id that was just emitted.
        """
        transition_tokens = self._stage_transition_tokens.get(
            self.current_stage
        )
        if transition_tokens is not None and (
            token in transition_tokens or not len(transition_tokens)
        ):
            self.__current_stage_idx += 1

    @property
    def current_stage(self) -> StateStage:
        """StateStage : The stage generation is currently in."""
        return self._stages[self.__current_stage_idx]

    @current_stage.setter
    def current_stage(self, stage: StateStage) -> None:
        """Jump directly to `stage`, bypassing the normal transitions.

        Parameters
        ----------
        stage : StateStage
            The stage to jump to.

        Raises
        ------
        ValueError
            If `stage` is not in `_stages`.
        """
        self.__current_stage_idx = self._stages.index(stage)

    def get_allowed_tokens(self) -> Optional[List[int]]:
        """Return the tokens allowed at the current stage.

        Returns
        -------
        list of int, optional
            The allowed token ids, or `None` if the current stage signals
            end-of-generation (no constraint applies because generation
            is over).
        """
        return self._stage_allowed_tokens.get(self.current_stage)

    def update_last_token(self, token: int) -> None:
        """Advance the state machine after `token` was emitted.

        Parameters
        ----------
        token : int
            The token id that was just emitted.
        """
        self._advance_stage(token)
