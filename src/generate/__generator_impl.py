from src.constrainer.constrainer import Constrainer
from src.constrainer.constrainer_factory import ConstrainerFactory
from src.state import StateFactory, StateType, State
from src.models.function import Parameter, ParameterType, Function
from .generator_exceptions import GenerationError
from typing import List, Optional, Callable, Union
from .generator import Generator


class GeneratorImpl(Generator):

    def __strip_completion(self, completion: str) -> str:
        name_length = len(completion)
        while completion.endswith((",", '"', "'", " ", "}", "\n")):
            completion = completion[: name_length - 1]
            name_length -= 1
        while completion.startswith((" ", '"', "'", "\n")):
            completion = completion[1:]
        return completion

    def __get_next_token(
        self, result: List[int], constrainer: Constrainer
    ) -> Optional[int]:
        logits = self.model.get_logits_from_input_ids(result)
        constrained_logits = constrainer.constrain_logits(logits)
        token = constrainer.pick_token(constrained_logits)
        return token

    def __get_completion(self, prompt: str, constrainer: Constrainer) -> str:
        result: List[int] = self.tokenizer.encode(prompt).tolist()[0]
        initial_len = len(result)
        token = self.__get_next_token(result, constrainer)
        while token is not None:
            result.append(token)
            token = self.__get_next_token(result, constrainer)
        return self.tokenizer.decode(result[initial_len:])

    def generate_name(self, prompt: str, functions: List[Function]) -> str:
        print("Generating name...")

        prompt += "\nPick the function to run from the following options:\n\n"
        prompt += "\n".join(
            [
                f" - {function.name}: {function.description}"
                for function in functions
            ]
        )
        prompt += '\n\n {"function": { "name": "'

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
        print("Generating parameters")

        parameters: List[Parameter] = []
        prompt += "\nPick the parameters for this function:"
        prompt += f"{function.name}: {function.description}"
        prompt += '\n{"function": { "name": "'
        prompt += f'{function.name}", "parameters: [\n'
        for parameter in function.parameters:
            parameter_type = parameter.type.value
            if parameter.type == ParameterType.FLOAT:
                parameter_type = "float"
            prompt += "\n{\t" + f'"name": {parameter.name}",\n\t"type": "{
                    parameter_type
                }",\n\t"value": "'

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
            prompt += result + '"\n},'
            stripped_result = self.__strip_completion(result)
            if value_parser is not None:
                try:
                    value_parser(stripped_result)
                except ValueError:
                    raise GenerationError(
                        "Invalid value for parameter of type",
                        f"{parameter.type}: {stripped_result}",
                    )
            parameters.append(
                Parameter(
                    name=parameter.name,
                    type=parameter.type,
                    value=stripped_result,
                )
            )

        return parameters
