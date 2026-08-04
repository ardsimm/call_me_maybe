from src.model.model import Model
from src.tokenize import TokenizerFactory, TokenizerType
from typing import Optional
from .generator import Generator
from .__generator_impl import GeneratorImpl


class GeneratorFactory:

    __generator_instance: Optional[Generator] = None

    @classmethod
    def get_instance(cls) -> Generator:
        if cls.__generator_instance is None:
            model = Model.get_instance()
            cls.__generator_instance = GeneratorImpl(
                model,
                TokenizerFactory.get_instance(TokenizerType.DEFAULT, model),
            )
        return cls.__generator_instance
