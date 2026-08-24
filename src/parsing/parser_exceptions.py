from typing import List
from pydantic_core import ErrorDetails


class ParsingError(ValueError):
    """Raised when CLI arguments or an input JSON file cannot be parsed."""

    pass


class ParsingValidationError(ParsingError):
    """Raised when parsed input fails pydantic schema validation.

    Parameters
    ----------
    validation_errors : list of ErrorDetails
        The `pydantic_core.ErrorDetails` entries from the failed
        validation, each contributing one line to the exception message.
    """

    def __init__(self, validation_errors: List[ErrorDetails]):
        message = (
            f"{len(validation_errors)} "
            + "Validation error(s) occured during parsing:\n"
            + "\n"
            + "\n".join([error.get("msg") for error in validation_errors])
        )
        super().__init__(message)
