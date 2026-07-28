from src.constrainer.constrainer import Constrainer
from src.constrainer.constrainer_factory import ConstrainerFactory
from src.constrainer.constrainer_type import ConstrainerType
from src.state.state_factory import StateFactory
from src.state.state_type import StateType

from .generator import Generator
from ..models.function import Parameter, ParameterType, Function
from typing import List, Optional


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
            self,
            result: List[int],
            constrainer: Constrainer
    ) -> Optional[int]:
        logits = self.model.get_logits_from_input_ids(result)
        constrained_logits = constrainer.constrain_logits(logits)
        token = constrainer.pick_token(constrained_logits)
        return token

    def __get_completion(
        self,
        prompt: str,
        constrainer: Constrainer
    ) -> str:
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
                type=ConstrainerType.GENERIC,
                state=StateFactory.get_instance(StateType.STRING_STATE)
            )
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
            state_type: StateType
            prompt += "\n{\t" + f'"name": {parameter.name}",\n\t"type": "{
                    parameter.type.value
                }",\n\t"value": "'

            if parameter.type == ParameterType.STRING:
                state_type = StateType.STRING_STATE
            if parameter.type == ParameterType.INT:
                state_type = StateType.INT_STATE
            elif parameter.type == ParameterType.FLOAT:
                state_type = StateType.FLOAT_STATE
            elif parameter.type == ParameterType.BOOL:
                raise ValueError("Parameter type bool not yet supported")

            result = self.__get_completion(
                prompt=prompt,
                constrainer=ConstrainerFactory.get_instance(
                    ConstrainerType.GENERIC,
                    StateFactory.get_instance(state_type)
                )
            )
            prompt += result + '"\n},'
            parameters.append(
                Parameter(
                    name=parameter.name,
                    type=parameter.type,
                    value=self.__strip_completion(result),
                )
            )

        return parameters
