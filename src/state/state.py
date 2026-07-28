from enum import Enum
from typing import Dict, List, Optional

from llm_sdk import Small_LLM_Model

from src.tokenize.tokenizer import Tokenizer
from src.tokenize.tokenizer_factory import TokenizerFactory
from src.tokenize.tokenizer_type import TokenizerType


class StateStage(Enum):
    pass


class State:

    _stages: List[StateStage]
    __current_stage_idx: int
    _tokenizer: Tokenizer
    _stage_allowed_tokens: Dict[StateStage, Optional[List[int]]]
    _stage_transition_tokens: Dict[StateStage, List[int]]

    def __init__(self) -> None:
        self._tokenizer = TokenizerFactory.get_instance(
            TokenizerType.DEFAULT, Small_LLM_Model()
        )
        self.__current_stage_idx = 0

    @property
    def current_stage(self) -> StateStage:
        return self._stages[self.__current_stage_idx]

    def get_allowed_tokens(self) -> Optional[List[int]]:
        return self._stage_allowed_tokens.get(self.current_stage)

    def update_last_token(self, token: int) -> None:
        transition_tokens = self._stage_transition_tokens.get(
            self.current_stage
        )
        if transition_tokens is not None and (
            token in transition_tokens or not len(transition_tokens)
        ):
            self.__current_stage_idx += 1
