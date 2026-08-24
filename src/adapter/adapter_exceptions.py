class AdapterException(ValueError):
    """Base class for errors raised by an `Adapter` implementation.

    Extends `ValueError` (not `Exception`) so that any existing
    `except ValueError` clause around adapter calls also catches these
    without change.
    """

    pass


class SerializationException(AdapterException):
    """Raised when an `Adapter` fails to serialize a value."""

    pass


class DeserializationException(AdapterException):
    """Raised when an `Adapter` fails to parse encoded data."""

    pass
