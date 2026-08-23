from typing import Optional
from .generator import Generator
from .__generator_impl import GeneratorImpl


class GeneratorFactory:

    __generator_instance: Optional[Generator] = None

    @classmethod
    def get_instance(cls) -> Generator:
        if cls.__generator_instance is None:
            cls.__generator_instance = GeneratorImpl()
        return cls.__generator_instance
