from abc import abstractmethod, ABC


class Adapter(ABC):
    """Converts between Python values and a serialized text format."""

    @abstractmethod
    def serialize(self, value: object) -> str:
        """Serialize a Python value to text.

        Parameters
        ----------
        value : object
            The value to serialize.

        Returns
        -------
        str
            The serialized text.

        Raises
        ------
        SerializationException
            If `value` cannot be serialized.
        """
        pass

    @abstractmethod
    def parse(self, data: str) -> object:
        """Parse text into a Python value.

        Parameters
        ----------
        data : str
            The text to parse.

        Returns
        -------
        object
            The parsed value.

        Raises
        ------
        DeserializationException
            If `data` cannot be parsed.
        """
        pass
