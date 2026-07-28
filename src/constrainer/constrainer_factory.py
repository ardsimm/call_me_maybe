from src.state.state import State

from .constrainer import Constrainer
from .constrainer_type import ConstrainerType
from .__boolean_constrainer import BooleanConstrainer
from .__function_name_constrainer import FunctionNameConstrainer
from .__generic_constrainer import GenericConstrainer


class ConstrainerFactory:

    @staticmethod
    def get_instance(type: ConstrainerType, state: State) -> Constrainer:
        if type == ConstrainerType.GENERIC:
            return GenericConstrainer(state)
        if type == ConstrainerType.BOOLEAN:
            return BooleanConstrainer(state)
        if type == ConstrainerType.FUNCTION_NAME:
            return FunctionNameConstrainer(state)
        raise ValueError(f"Invalid constrainer type {type}")
