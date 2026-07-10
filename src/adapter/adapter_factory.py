from .__json_adapter import JSONAdapter
from .adapter_type import AdapterType
from .adapter import Adapter
from typing import Optional


class AdapterFactory:

    __json_adapter_instance: Optional[JSONAdapter] = None

    @classmethod
    def get_instance(cls, type: AdapterType) -> Adapter:
        if type == AdapterType.JSON:
            if cls.__json_adapter_instance is None:
                cls.__json_adapter_instance = JSONAdapter()
            return cls.__json_adapter_instance
        else:
            raise ValueError(f"Invalid adapter type {type.name}")
