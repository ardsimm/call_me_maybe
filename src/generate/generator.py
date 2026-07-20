from abc import ABC, abstractmethod
from llm_sdk import Small_LLM_Model
from ..tokenize import Tokenizer
from ..models import OutputItem, Function
from typing import List


class Generator(ABC):

    __model: Small_LLM_Model
    __tokenizer: Tokenizer

    def __init__(self, model: Small_LLM_Model, tokenizer: Tokenizer) -> None:
        self.__model = model
        self.__tokenizer = tokenizer

    @property
    def model(self) -> Small_LLM_Model:
        return self.__model

    @model.setter
    def model(self, model: Small_LLM_Model) -> None:
        if model is None or not isinstance(model, Small_LLM_Model):
            raise ValueError("Invalid type for model attribute")
        self.__model = model

    @property
    def tokenizer(self) -> Tokenizer:
        return self.__tokenizer

    @tokenizer.setter
    def tokenizer(self, tokenizer: Tokenizer) -> None:
        if tokenizer is None or not isinstance(tokenizer, Tokenizer):
            raise ValueError("Invalid type for attribute tokenizer")
        self.__tokenizer = tokenizer

    @abstractmethod
    def get_next_item(
        self, prompt: str, functions: List[Function]
    ) -> OutputItem:
        pass
