from .adapter import Adapter
import json


class JSONAdapter(Adapter):

    def serialize(self, value: object) -> str:
        return json.dumps(value)

    def parse(self, data: str) -> object:
        return json.loads(data)
