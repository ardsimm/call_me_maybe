from abc import ABC, abstractmethod
from typing import List
from torch import Tensor
from src.model.model import Model


class Tokenizer(ABC):

    __model: Model

    def __init__(self, model: Model) -> None:
        self.__model = model

    @property
    def model(self) -> Model:
        return self.__model

    @model.setter
    def model(self, model: Model) -> None:
        self.__model = model

    @abstractmethod
    def encode(self, data: str) -> Tensor:
        pass

    @abstractmethod
    def decode(self, data: List[int]) -> str:
        pass
