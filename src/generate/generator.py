from abc import ABC, abstractmethod
from src.model import Model

from src.tokenize import Tokenizer
from src.models import Function, Parameter
from typing import List

from src.tokenize.tokenizer_factory import TokenizerFactory
from src.tokenize.tokenizer_type import TokenizerType


class Generator(ABC):
    """Turns a user prompt into a function name, then its parameters.

    Concrete implementations drive the constrained-decoding pipeline
    (`Constrainer` + `State`) to keep every generated token grammar-valid.
    """

    __model: Model
    __tokenizer: Tokenizer

    def __init__(self) -> None:
        """Fetch the singleton `Model` and the default `Tokenizer`."""
        self.__model = Model.get_instance()
        self.__tokenizer = TokenizerFactory.get_instance(
            TokenizerType.DEFAULT,
        )

    @property
    def model(self) -> Model:
        """Model : The model this generator decodes with."""
        return self.__model

    @property
    def tokenizer(self) -> Tokenizer:
        """Tokenizer : The tokenizer this generator encodes/decodes with."""
        return self.__tokenizer

    @abstractmethod
    def generate_name(self, prompt: str, functions: List[Function]) -> str:
        """Generate the name of the function `prompt` should call.

        Parameters
        ----------
        prompt : str
            The user's natural-language request.
        functions : list of Function
            Every candidate function the model may choose among.

        Returns
        -------
        str
            The chosen function's name.
        """
        pass

    @abstractmethod
    def generate_parameters(
        self, prompt: str, function: Function
    ) -> List[Parameter]:
        """Generate a value for each of `function`'s parameters.

        Parameters
        ----------
        prompt : str
            The user's natural-language request.
        function : Function
            The function whose parameters should be filled in, one at a
            time, each generation threading the prior ones as context.

        Returns
        -------
        list of Parameter
            One `Parameter` per `function.parameters`, in order, with
            `value` set from generation.
        """
        pass
