from .tokenizer import Tokenizer
from typing import Optional
from llm_sdk import Small_LLM_Model
from .tokenizer_type import TokenizerType
from .__default_tokenizer import DefaultTokenizer


class TokenizerFactory:

    __default_tokenizer_instance: Optional[DefaultTokenizer] = None

    @classmethod
    def get_instance(
        cls, type: TokenizerType, model: Small_LLM_Model
    ) -> Tokenizer:
        if type == TokenizerType.DEFAULT:
            if cls.__default_tokenizer_instance is None:
                cls.__default_tokenizer_instance = DefaultTokenizer(model)
            return cls.__default_tokenizer_instance
        raise ValueError(f"Invalid tokenizer type {type.name}")
