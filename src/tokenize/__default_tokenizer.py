from .tokenizer import Tokenizer
from torch import Tensor
from typing import List


class DefaultTokenizer(Tokenizer):

    def encode(self, data: str) -> Tensor:
        return self.model.encode(data)

    def decode(self, data: List[int]) -> str:
        return self.model.decode(data)
