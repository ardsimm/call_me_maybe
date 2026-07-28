import json
from typing import Dict, List
import re
from src.generate.generation_error import GenerationError
from src.model.model_wrapper import ModelWrapper
from .state import StateStage, State


class StringStateStage(StateStage):
    INITIAL = 0,
    DATA = 1,
    TERMINAL = 2


class StringState(State):

    def __init__(self) -> None:
        super().__init__()
        model = ModelWrapper.get_instance()
        string_end_sequences: List[int] = []
        try:
            with open(model.get_path_to_vocab_file()) as vocab_file:
                vocab_dict: Dict[str, int] = json.loads(vocab_file.read())
            for key, token_id in vocab_dict.items():
                if re.search(r'(?<!\\)"', key):
                    string_end_sequences.append(token_id)
        except FileNotFoundError as e:
            raise GenerationError(f"Failed to open vocab file: {e}")
        except json.JSONDecodeError as e:
            raise GenerationError(f"Failed to parse vocab file: {e}")

        self._stages = [
            StringStateStage.INITIAL,
            StringStateStage.DATA,
            StringStateStage.TERMINAL,
        ]
        self._stage_allowed_tokens = {
            StringStateStage.INITIAL: [],
            StringStateStage.DATA: [],
            StringStateStage.TERMINAL: None,
        }
        self._stage_transition_tokens = {
            StringStateStage.INITIAL: [],
            StringStateStage.DATA: string_end_sequences,
        }
