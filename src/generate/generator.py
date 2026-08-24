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

    @property
    def tokenizer(self) -> Tokenizer:
        return self.__tokenizer

    @abstractmethod
    def generate_name(self, prompt: str, functions: List[Function]) -> str:
        pass

    @abstractmethod
    def generate_parameters(
        self, prompt: str, function: Function
    ) -> List[Parameter]:
        pass
