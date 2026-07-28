from .generator import Generator
from ..models.function import Parameter, ParameterType, Function
from typing import Any, Callable, List, Set


class GeneratorImpl(Generator):

    def __strip_completion(self, completion: str) -> str:
        name_length = len(completion)
        while completion.endswith((",", '"', "'", " ", "}", "\n")):
            completion = completion[: name_length - 1]
            name_length -= 1
        while completion.startswith((" ", '"', "'", "\n")):
            completion = completion[1:]
        return completion

    def __get_completion(
        self,
        prompt: str,
        detect_end: Callable[[List[int], int], bool],
        valid_tokens: Set[int] = set(),
    ) -> str:
        result: List[int] = self.tokenizer.encode(prompt).tolist()[0]
        initial_len = len(result)
        result_len = initial_len
        while initial_len == result_len or not detect_end(result, initial_len):
            logits = self.model.get_logits_from_input_ids(result)
            max_logit_index = logits.index(max(logits))
            while len(valid_tokens) and max_logit_index not in valid_tokens:
                logits[max_logit_index] = -1
                max_logit_index = logits.index(max(logits))
            result.append(max_logit_index)
            result_len += 1
        return self.tokenizer.decode(result[initial_len:])

    def __flatten_list(self, list: List[List[Any]]) -> List[Any]:
        flattened: List[Any] = []
        for el in list:
            flattened.extend(el)
        return flattened

    def generate_name(self, prompt: str, functions: List[Function]) -> str:
        print("Generating name...")

        end_tokens: List[int] = self.tokenizer.encode('"').tolist()[0]

        prompt += "\nPick the function to run from the following options:\n\n"
        prompt += "\n".join(
            [
                f" - {function.name}: {function.description}"
                for function in functions
            ]
        )
        prompt += '\n\n {"function": { "name": "'

        valid_tokens = set()
        valid_tokens.update(
            self.__flatten_list(
                [
                    self.model.encode(function.name).tolist()[0]
                    for function in functions
                ]
            )
        )
        valid_tokens.update(end_tokens)

        def detect_name_end(tokens: List[int], _: int) -> bool:
            return tokens[len(tokens) - 1] in end_tokens

        result = self.__get_completion(prompt, detect_name_end, valid_tokens)
        return self.__strip_completion(result)

    def generate_parameters(
        self, prompt: str, function: Function
    ) -> List[Parameter]:
        print("Generating parameters")

        def detect_end(tokens: List[int], initial_len: int) -> bool:
            return '"' in self.tokenizer.decode(tokens[initial_len:])

        parameters: List[Parameter] = []
        prompt += "\nPick the parameters for this function:"
        prompt += f"{function.name}: {function.description}"
        prompt += '\n{"function": { "name": "'
        prompt += f'{function.name}", "parameters: [\n'
        for parameter in function.parameters:
            prompt += "\n{\t" + f'"name": {parameter.name}",\n\t"type": "{
                    parameter.type.value[0]
                }",\n\t"value": "'
            valid_tokens: Set[int] = set()

            if parameter.type == ParameterType.INT:
                valid_tokens.update(
                    self.__flatten_list(
                        [
                            self.tokenizer.encode(char).tolist()[0]
                            for char in '0123456789"'
                        ]
                    ),
                )
            elif parameter.type == ParameterType.FLOAT:
                valid_tokens.update(
                    self.__flatten_list(
                        [
                            self.tokenizer.encode(char).tolist()[0]
                            for char in '0123456789."'
                        ]
                    ),
                )
            elif parameter.type == ParameterType.BOOL:
                valid_tokens.update(
                    self.__flatten_list(
                        [
                            self.tokenizer.encode(char).tolist()[0]
                            for char in '01"'
                        ]
                    ),
                )

            result = self.__get_completion(
                prompt=prompt,
                valid_tokens=valid_tokens,
                detect_end=detect_end,
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
