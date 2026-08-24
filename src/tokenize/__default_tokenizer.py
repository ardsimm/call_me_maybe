from .tokenizer import Tokenizer
from torch import Tensor
from typing import List


class DefaultTokenizer(Tokenizer):
    """`Tokenizer` that forwards directly to `Model.encode`/`Model.decode`."""

    def encode(self, data: str) -> Tensor:
        """Tokenize text via `model.encode`.

        Parameters
        ----------
        data : str
            The text to tokenize.

        Returns
        -------
        Tensor
            The resulting token ids.

        Raises
        ------
        Exception
            Any exception raised by `model.encode` propagates uncaught.
        """
        return self.model.encode(data)

    def decode(self, data: List[int]) -> str:
        """Convert token ids back into text via `model.decode`.

        Parameters
        ----------
        data : list of int
            The token ids to decode.

        Returns
        -------
        str
            The decoded text.

        Raises
        ------
        Exception
            Any exception raised by `model.decode` propagates uncaught.
        """
        return self.model.decode(data)
