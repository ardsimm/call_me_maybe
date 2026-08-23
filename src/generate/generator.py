from abc import ABC, abstractmethod
from src.model import Model

from src.tokenize import Tokenizer
from src.models import Function, Parameter
from typing import List

from src.tokenize.tokenizer_factory import TokenizerFactory
from src.tokenize.tokenizer_type import TokenizerType


class Generator(ABC):

    __model: Model
    __tokenizer: Tokenizer

    def __init__(self) -> None:
        self.__model = Model.get_instance()
        self.__tokenizer = TokenizerFactory.get_instance(
            TokenizerType.DEFAULT,
        )

    @property
    def model(self) -> Model:
        return self.__model

    @model.setter
    def model(self, model: Model) -> None:
        if model is None or not isinstance(model, Model):
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
    def generate_name(self, prompt: str, functions: List[Function]) -> str:
        pass

    @abstractmethod
    def generate_parameters(
        self, prompt: str, function: Function
    ) -> List[Parameter]:
        pass
