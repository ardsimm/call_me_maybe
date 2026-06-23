from state import State


class StateFactory:

    __state_instance: State

    @staticmethod
    def get_instance() -> State:
        raise NotImplementedError(
            "Method get_instance of StateFactory" + " not yet implemented"
        )
