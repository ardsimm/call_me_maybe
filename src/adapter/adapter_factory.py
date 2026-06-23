from adapter import Adapter
from typing import Any


class AdapterFactory:

    __adapter_instance: Adapter

    @staticmethod
    def get_instance(type: Any) -> Adapter:
        raise NotImplementedError(
            "Method get_instance of AdapterFactory" + " not yet implemented"
        )
