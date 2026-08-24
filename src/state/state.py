from enum import Enum
from typing import Dict, List, Optional
from src.tokenize.tokenizer import Tokenizer
from src.tokenize.tokenizer_factory import TokenizerFactory
from src.tokenize.tokenizer_type import TokenizerType


class StateStage(Enum):
    pass


class State:

    _stages: List[StateStage]
    _tokenizer: Tokenizer
    _stage_allowed_tokens: Dict[StateStage, Optional[List[int]]]
    _stage_transition_tokens: Dict[StateStage, List[int]]
    __current_stage_idx: int

    def __init__(self) -> None:
        self._tokenizer = TokenizerFactory.get_instance(TokenizerType.DEFAULT)
        self.__current_stage_idx = 0

    def _advance_stage(self, token: int) -> None:
        transition_tokens = self._stage_transition_tokens.get(
            self.current_stage
        )
        if transition_tokens is not None and (
            token in transition_tokens or not len(transition_tokens)
        ):
            self.__current_stage_idx += 1
            print("Current stage:", self.current_stage.name)

    @property
    def current_stage(self) -> StateStage:
        return self._stages[self.__current_stage_idx]

    @current_stage.setter
    def current_stage(self, stage: StateStage) -> None:
        self.__current_stage_idx = self._stages.index(stage)
        print("Current stage:", self.current_stage.name)

    def get_allowed_tokens(self) -> Optional[List[int]]:
        return self._stage_allowed_tokens.get(self.current_stage)

    def update_last_token(self, token: int) -> None:
        self._advance_stage(token)
