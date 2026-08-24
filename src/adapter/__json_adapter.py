from src.adapter.adapter_exceptions import (
    DeserializationException,
    SerializationException,
)
from .adapter import Adapter
import json


class JSONAdapter(Adapter):

    def serialize(self, value: object) -> str:
        dump: str
        try:
            dump = json.dumps(value)
        except TypeError as e:
            raise SerializationException(e)
        return dump

    def parse(self, data: str) -> object:
        load: object
        try:
            load = json.loads(data)
        except json.JSONDecodeError as e:
            raise DeserializationException(e)
        return load
