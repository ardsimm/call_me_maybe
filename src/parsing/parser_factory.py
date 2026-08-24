from typing import Optional

from .parser import Parser
from .__argument_parser import ArgumentParser


class ParserFactory:
    """Builds/caches the singleton `Parser` instance."""

    __parser_instance: Optional[Parser] = None

    @classmethod
    def get_instance(cls) -> Parser:
        """Get the singleton `Parser`, creating it if needed.

        Returns
        -------
        Parser
            The singleton `ArgumentParser` instance.
        """
        if cls.__parser_instance is None:
            cls.__parser_instance = ArgumentParser()
        return cls.__parser_instance
