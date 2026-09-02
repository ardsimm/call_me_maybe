import json
import re
from typing import Dict, Optional, Set
from llm_sdk import Small_LLM_Model
from src.adapter.adapter_exceptions import DeserializationException
from src.generate.generator_exceptions import GenerationError


class Model(Small_LLM_Model):
    """Singleton wrapper around `llm_sdk.Small_LLM_Model`.

    Adds `string_end_sequences`: every vocab token whose surface text
    contains an unescaped double quote, used by every `State` to know which
    tokens legally close a generated JSON string.
    """

    __instance: Optional["Model"] = None
    __string_end_sequences: Optional[Set[int]] = None

    def __load_string_end_sequences(self) -> None:
        """Compute and cache `string_end_sequences` from the vocab file.

        Raises
        ------
        GenerationError
            If the vocab file cannot be opened, read, or parsed, or if any
            other error occurs while scanning it -- every exception raised
            while loading is converted to `GenerationError`.
        """
        self.__string_end_sequences = set()
        try:
            with open(self.get_path_to_vocab_file()) as vocab_file:
                vocab_dict: Dict[str, int] = json.loads(vocab_file.read())
            for key, token_id in vocab_dict.items():
                if re.search(r'(?<!\\)"', key):
                    self.__string_end_sequences.add(token_id)
        except IOError as e:
            raise GenerationError(f"Failed to open vocab file: {e}")
        except DeserializationException as e:
            raise GenerationError(f"Failed to parse vocab file: {e}")
        except Exception as e:
            raise GenerationError(
                "An unknown error occured while loading "
                + f" string end sequences: {e}"
            )

    @property
    def string_end_sequences(self) -> Set[int]:
        """list of int : Token ids whose text contains an unescaped `"`.

        Computed once from the vocab file and cached.

        Raises
        ------
        GenerationError
            Forwarded from `__load_string_end_sequences` on first access if
            the vocab file cannot be loaded.
        """
        if self.__string_end_sequences is None:
            self.__load_string_end_sequences()
        assert self.__string_end_sequences is not None
        return self.__string_end_sequences

    @classmethod
    def get_instance(cls) -> "Model":
        """Get the singleton `Model`, creating it if needed.

        Returns
        -------
        Model
            The singleton model instance.

        Raises
        ------
        Exception
            Any exception raised by `Small_LLM_Model.__init__` the first
            time (e.g. model download/load failure) propagates uncaught.
        """
        if cls.__instance is None:
            cls.__instance = Model()
        return cls.__instance
