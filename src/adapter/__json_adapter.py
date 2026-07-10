from .adapter import Adapter
import json


class JSONAdapter(Adapter):

    def serialize(self, value: object) -> str:
        if not isinstance(value, dict):
            raise ValueError("Cannot serialize non-dict object to JSON")
        return json.dumps(value)

    def parse(self, data: str) -> object:
        return json.loads(data)
