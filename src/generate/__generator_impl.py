from src.constrainer.constrainer import Constrainer
from src.constrainer.constrainer_factory import ConstrainerFactory
from src.prompting.prompting import Prompting
from src.state import StateFactory, StateType, State
from src.models.function import Parameter, ParameterType, Function
from .generator_exceptions import GenerationError
from typing import List, Optional, Callable, Union
from .generator import Generator


class GeneratorImpl(Generator):

    def __find_unescapted_quote_idx(self, s: str) -> int:
        idx = 0
        escape_count = 0
        for char in s:
            if char == "\\":
                escape_count += 1
            if char == "\"" and not escape_count % 2:
                return idx
            elif char == "\"":
                escape_count = 0
            idx += 1
        return -1

    def __strip_completion(self, completion: str) -> str:
        return completion[:self.__find_unescapted_quote_idx(completion)]

    def __get_next_token(
        self, result: List[int], constrainer: Constrainer
    ) -> Optional[int]:
        return constrainer.pick_token(
            self.model.get_logits_from_input_ids(result)
        )

    def __get_completion(self, prompt: str, constrainer: Constrainer) -> str:
        print(
            "Getting completion for prompt:",
            prompt,
            "---------------",
            sep="\n",
        )
        result: List[int] = self.tokenizer.encode(prompt).tolist()[0]
        initial_len = len(result)
        token = self.__get_next_token(result, constrainer)
        while token is not None:
            print("Generated:", self.model.decode([token]))
            result.append(token)
            token = self.__get_next_token(result, constrainer)
        return self.tokenizer.decode(result[initial_len:])

    def generate_name(self, prompt: str, functions: List[Function]) -> str:
        print(
            "------------------",
            "Generating name...",
            "------------------",
            sep="\n",
        )

        prompt = Prompting.build_name_generation_prompt(prompt, functions)

        result = self.__get_completion(
            prompt=prompt,
            constrainer=ConstrainerFactory.get_instance(
                StateFactory.get_trie_state_instance(
                    [
                        self.tokenizer.encode(function.name).tolist()[0]
                        for function in functions
                    ]
                )
            ),
        )
        return self.__strip_completion(result)

    def generate_parameters(
        self, prompt: str, function: Function
    ) -> List[Parameter]:
        print(
            "---------------------",
            "Generating parameters",
            "---------------------",
            sep="\n",
        )

        parameters: List[Parameter] = []
        user_prompt = prompt
        last_parameter: Optional[Parameter] = None
        prompt = Prompting.build_parameter_generation_prompt(
            user_prompt, function
        )
        for parameter in function.parameters:
            parameter.value = None
            prompt = Prompting.build_next_parameter_generation_prompt(
                prompt, function, parameter, last_parameter
            )
            value_parser: Optional[
                Callable[[str], Union[int, float, bool]]
            ] = None
            state: State = StateFactory.get_instance(StateType.STRING_STATE)
            if parameter.type == ParameterType.INT:
                state = StateFactory.get_instance(StateType.INT_STATE)
                value_parser = int
            elif parameter.type == ParameterType.FLOAT:
                state = StateFactory.get_instance(StateType.FLOAT_STATE)
                value_parser = float
            elif parameter.type == ParameterType.BOOL:
                state = StateFactory.get_trie_state_instance(
                    [
                        self.tokenizer.encode(value).tolist()[0]
                        for value in ["true", "false"]
                    ]
                )
                value_parser = bool

            result = self.__get_completion(
                prompt=prompt,
                constrainer=ConstrainerFactory.get_instance(state),
            )
            stripped_result = self.__strip_completion(result)
            if value_parser is not None:
                try:
                    value_parser(stripped_result)
                except ValueError:
                    raise GenerationError(
                        "Invalid value for parameter of type"
                        + f" {parameter.type.value}: {stripped_result}",
                    )
            parameter.value = stripped_result
            last_parameter = Parameter(
                name=parameter.name, type=parameter.type, value=parameter.value
            )
            parameters.append(last_parameter)

        return parameters
