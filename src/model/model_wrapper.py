from typing import Optional

from llm_sdk import Small_LLM_Model


class ModelWrapper:
    __model: Optional[Small_LLM_Model] = None

    @classmethod
    def get_instance(cls) -> Small_LLM_Model:
        if cls.__model is None:
            cls.__model = Small_LLM_Model()
        return cls.__model
