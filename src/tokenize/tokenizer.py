from abc import ABC, abstractmethod
from typing import List
from torch import Tensor
from src.model.model import Model


class Tokenizer(ABC):
    """Encodes/decodes text against a `Model`'s vocabulary.

    Kept as a thin, swappable ABC so implementations can eventually stop
    depending on the SDK's `encode`/`decode` and rebuild tokenization from
    `get_logits_from_input_ids`/`get_path_to_vocab_file` alone.
    """

    __model: Model

    def __init__(self, model: Model) -> None:
        """Store the `Model` this tokenizer encodes/decodes against.

        Parameters
        ----------
        model : Model
            The model whose vocabulary this tokenizer uses.
        """
        self.__model = model

    @property
    def model(self) -> Model:
        """Model : The model this tokenizer encodes/decodes against."""
        return self.__model

    @abstractmethod
    def encode(self, data: str) -> Tensor:
        """Encode `data` into a tensor of token ids."""
        pass

    @abstractmethod
    def decode(self, data: List[int]) -> str:
        """Decode a list of token ids back into text."""
        pass
