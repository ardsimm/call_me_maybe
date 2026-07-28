from src.generate.__generator_impl import GeneratorImpl
from src.model.model_wrapper import ModelWrapper
from .generator import Generator
from src.tokenize import TokenizerFactory, TokenizerType
from typing import Optional


class GeneratorFactory:

    __generator_instance: Optional[Generator] = None

    @classmethod
    def get_instance(cls) -> Generator:
        if cls.__generator_instance is None:
            model = ModelWrapper.get_instance()
            cls.__generator_instance = GeneratorImpl(
                model,
                TokenizerFactory.get_instance(TokenizerType.DEFAULT, model),
            )
        return cls.__generator_instance
