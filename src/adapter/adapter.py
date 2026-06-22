from abc import abstractmethod, ABC


class Adapter(ABC):

    @abstractmethod
    def serialize(self, value: object) -> str:
        pass

    @abstractmethod
    def parse(self, data: str) -> object:
        pass
