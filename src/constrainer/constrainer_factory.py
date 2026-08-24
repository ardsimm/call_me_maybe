from src.state.state import State

from .constrainer import Constrainer
from .__constrainer_impl import ConstrainerImpl


class ConstrainerFactory:
    """Builds `Constrainer` instances."""

    @staticmethod
    def get_instance(state: State) -> Constrainer:
        """Build a new `Constrainer` bound to `state`.

        Parameters
        ----------
        state : State
            The state machine the constrainer will consult and advance.

        Returns
        -------
        Constrainer
            A new `ConstrainerImpl` bound to `state`.
        """
        return ConstrainerImpl(state)
