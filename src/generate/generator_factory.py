from typing import Optional
from .generator import Generator
from .__generator_impl import GeneratorImpl


class GeneratorFactory:
    """Builds/caches the singleton `Generator` instance."""

    __generator_instance: Optional[Generator] = None

    @classmethod
    def get_instance(cls) -> Generator:
        """Get the singleton `Generator`, creating it if needed.

        Returns
        -------
        Generator
            The singleton `GeneratorImpl` instance.

        Raises
        ------
        Exception
            Any exception raised while constructing the underlying `Model`
            singleton the first time (e.g. model download/load failure)
            propagates uncaught.
        """
        if cls.__generator_instance is None:
            cls.__generator_instance = GeneratorImpl()
        return cls.__generator_instance
