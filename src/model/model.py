import json
import re
from typing import Dict, List, Optional
from llm_sdk import Small_LLM_Model
from src.generate.generation_error import GenerationError


class Model(Small_LLM_Model):

    __instance: Optional["Model"] = None
    __string_end_sequences: Optional[List[int]] = None

    def __load_string_end_sequences(self) -> None:
        self.__string_end_sequences = []
        try:
            with open(self.get_path_to_vocab_file()) as vocab_file:
                vocab_dict: Dict[str, int] = json.loads(vocab_file.read())
            for key, token_id in vocab_dict.items():
                if re.search(r'(?<!\\)"', key):
                    self.__string_end_sequences.append(token_id)
        except FileNotFoundError as e:
            raise GenerationError(f"Failed to open vocab file: {e}")
        except json.JSONDecodeError as e:
            raise GenerationError(f"Failed to parse vocab file: {e}")

    @property
    def string_end_sequences(self) -> List[int]:
        if self.__string_end_sequences is None:
            self.__load_string_end_sequences()
        assert self.__string_end_sequences is not None
        return self.__string_end_sequences

    @classmethod
    def get_instance(cls) -> "Model":
        if cls.__instance is None:
            cls.__instance = Model()
        return cls.__instance
