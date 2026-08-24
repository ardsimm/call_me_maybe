from abc import ABC, abstractmethod
from typing import Any
from src.models.arguments import Arguments


class Parser(ABC):
    """Builds a validated `Arguments` from some raw source."""

    @abstractmethod
    def parse(self, source: Any) -> Arguments:
        """Parse `source` into a validated `Arguments`.

        Parameters
        ----------
        source : Any
            The raw input to parse (e.g. a CLI argument list).

        Returns
        -------
        Arguments
            The validated arguments.

        Raises
        ------
        ParsingError
            If `source` cannot be parsed.
        ParsingValidationError
            If `source` parses but fails `Arguments`'s validation.
        """
        pass
