from .tokenizer import Tokenizer
from typing import Optional
from src.model import Model
from .tokenizer_type import TokenizerType
from .__default_tokenizer import DefaultTokenizer


class TokenizerFactory:
    """Builds/caches singleton `Tokenizer` instances per `TokenizerType`."""

    __default_tokenizer_instance: Optional[DefaultTokenizer] = None

    @classmethod
    def get_instance(cls, type: TokenizerType) -> Tokenizer:
        """Get the singleton `Tokenizer` for `type`, creating it if needed.

        Parameters
        ----------
        type : TokenizerType
            Which tokenizer implementation to return.

        Returns
        -------
        Tokenizer
            The singleton tokenizer instance for `type`, bound to the
            singleton `Model`.

        Raises
        ------
        ValueError
            If `type` is not a handled `TokenizerType` member.
        """
        if type == TokenizerType.DEFAULT:
            if cls.__default_tokenizer_instance is None:
                cls.__default_tokenizer_instance = DefaultTokenizer(
                    Model.get_instance()
                )
            return cls.__default_tokenizer_instance
        raise ValueError(f"Invalid tokenizer type {type.name}")
