from src.state.state import State

from .constrainer import Constrainer
from .__constrainer_impl import ConstrainerImpl


class ConstrainerFactory:

    @staticmethod
    def get_instance(state: State) -> Constrainer:
        return ConstrainerImpl(state)
