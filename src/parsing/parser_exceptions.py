from typing import List
from pydantic_core import ErrorDetails


class ParsingError(ValueError):
    pass


class ParsingValidationError(ParsingError):
    def __init__(self, validation_errors: List[ErrorDetails]):
        message = (
            f"{len(validation_errors)} "
            + "Validation error(s) occured during parsing:\n"
            + "\n"
            + "\n".join([error.get("msg") for error in validation_errors])
        )
        super().__init__(message)
