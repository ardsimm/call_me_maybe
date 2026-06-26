from abc import ABC, abstractmethod
from llm_sdk import Small_LLM_Model
from ..tokenize import Tokenizer
from typing import Dict


class Generator(ABC):

    _model: Small_LLM_Model
    _tokenizer: Tokenizer

    def __init__(self, tokenizer: Tokenizer) -> None:
        self.model = Small_LLM_Model()
        self.tokenizer = tokenizer

    @property
    def model(self) -> Small_LLM_Model:
        return self._model

    @model.setter
    def model(
        self,
        model: Small_LLM_Model
    ) -> None:
        if model is None or not isinstance(model, Small_LLM_Model):
            raise ValueError("Invalid type for model attribute")
        self._model = model

    @property
    def tokenizer(self) -> Tokenizer:
        return self._tokenizer

    @tokenizer.setter
    def tokenizer(
        self,
        tokenizer: Tokenizer
    ) -> None:
        if (
            tokenizer is None
            or not isinstance(tokenizer, Tokenizer)
        ):
            raise ValueError("Invalid type for attribute tokenizer")
        self._tokenizer = tokenizer

    @abstractmethod
    def generate_function_name(
        self,
        names: str,
        history: str
    ) -> str:
        pass

    @abstractmethod
    def generate_function_arguments(
        self,
        arguments: Dict[str, str],
        history: str
    ) -> str:
        pass
