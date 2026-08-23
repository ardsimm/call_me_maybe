from enum import Enum


class AdapterType(Enum):
    """The serialization formats `AdapterFactory` can build an `Adapter`
    for."""

    JSON = 0
