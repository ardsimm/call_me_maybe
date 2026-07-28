from abc import ABC, abstractmethod
from typing import List
from torch import Tensor
from llm_sdk import Small_LLM_Model


class Tokenizer(ABC):

    __model: Small_LLM_Model

    def __init__(self, model: Small_LLM_Model) -> None:
        self.__model = model

    @property
    def model(self) -> Small_LLM_Model:
        return self.__model

    @model.setter
    def model(self, model: Small_LLM_Model) -> None:
        self.__model = model

    @abstractmethod
    def encode(self, data: str) -> Tensor:
        pass

    @abstractmethod
    def decode(self, data: List[int]) -> str:
        pass
