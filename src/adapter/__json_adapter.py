from src.adapter.adapter_exceptions import (
    DeserializationException,
    SerializationException,
)
from .adapter import Adapter
import json


class JSONAdapter(Adapter):
    """`Adapter` backed by the standard library's `json` module."""

    def serialize(self, value: object) -> str:
        """Serialize a value to a JSON string via `json.dumps`.

        Parameters
        ----------
        value : object
            The value to serialize.

        Returns
        -------
        str
            The JSON-encoded text.

        Raises
        ------
        SerializationException
            If `value` is not JSON-serializable.
        TypeError
            `json.dumps` raises `TypeError` (not `JSONDecodeError`) for a
            non-serializable value, so it is not caught here and propagates
            uncaught.
        """
        dump: str
        try:
            dump = json.dumps(value)
        except TypeError as e:
            raise SerializationException(e)
        return dump

    def parse(self, data: str) -> object:
        """Parse a JSON string via `json.loads`.

        Parameters
        ----------
        data : str
            The JSON text to parse.

        Returns
        -------
        object
            The parsed value.

        Raises
        ------
        DeserializationException
            If `data` is not valid JSON.
        """
        load: object
        try:
            load = json.loads(data)
        except json.JSONDecodeError as e:
            raise DeserializationException(e)
        return load
