from .__json_adapter import JSONAdapter
from .adapter_type import AdapterType
from .adapter import Adapter
from typing import Optional


class AdapterFactory:
    """Builds/caches singleton `Adapter` instances per `AdapterType`."""

    __json_adapter_instance: Optional[JSONAdapter] = None

    @classmethod
    def get_instance(cls, type: AdapterType) -> Adapter:
        """Get the singleton `Adapter` for `type`, creating it if needed.

        Parameters
        ----------
        type : AdapterType
            Which adapter implementation to return.

        Returns
        -------
        Adapter
            The singleton adapter instance for `type`.

        Raises
        ------
        ValueError
            If `type` is not a handled `AdapterType` member.
        """
        if type == AdapterType.JSON:
            if cls.__json_adapter_instance is None:
                cls.__json_adapter_instance = JSONAdapter()
            return cls.__json_adapter_instance
        raise ValueError(f"Invalid adapter type {type.name}")
