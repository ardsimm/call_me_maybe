from abc import ABC
from llm_sdk.llm_sdk import Small_LLM_Model

class Generator(ABC):
    
    _model: Small_LLM_Model

    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model

    @property
    def model(self) -> Small_LLM_Model:
        return self._model

    @model.setter
    def model(self, model: Small_LLM_Model) -> None:
        if model is None or not isinstance(model, Small_LLM_Model):
            raise ValueError("Invalid type for model attribute")
        self._model = model
