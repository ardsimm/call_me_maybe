from src.generate.generation_error import GenerationError

from .generator import Generator
from ..models.function import Argument, ArgumentType, Function
from typing import List, Dict
from ..models.output_item import OutputItem
from functools import reduce


class GeneratorImpl(Generator):

    def __strip_completion(
        self,
        completion: str
    ) -> str:
        name_length = len(completion)
        while completion.endswith((",", '"', "'", " ", "}")):
            completion = completion[: name_length - 1]
            name_length -= 1
        while completion.startswith((" ", '"', "'")):
            completion = completion[1:]
        return completion

    def __get_name(
        self,
        prompt: str,
        functions: List[Function]
    ) -> str:
        print("\n====================")
        print("====================\n")
        print(f"Generating name for prompt: {prompt}")
        print("\n====================")
        print("====================\n")

        end_tokens: List[int] = self.tokenizer.encode('"').tolist()[0]

        prompt += "\nPick the function to run from the following options:\n\n"
        prompt += "\n".join([
            f" - {function.name}: {function.description}"
            for function in functions
        ])
        prompt += '\n\n {"function": { "name": "'

        result: List[int] = self.tokenizer.encode(prompt)[0].tolist()
        initial_len = len(result)
        logits: List[float]

        encoded_names = [
            self.model.encode(function.name).tolist()[0]
            for function in functions
        ]
        reduced_name_tokens: List[int] = reduce(
            lambda acc, el: acc + el,
            encoded_names,
            []
        )
        valid_tokens = set(reduced_name_tokens)
        valid_tokens.update(end_tokens)
        print(prompt, end="")
        while result[len(result) - 1] not in end_tokens:
            logits = self.model.get_logits_from_input_ids(result)
            max_logit_index = logits.index(max(logits))
            while max_logit_index not in valid_tokens:
                logits[max_logit_index] = -1
                max_logit_index = logits.index(max(logits))
            result.append(max_logit_index)
            print(self.model.decode(max_logit_index), end="")
        return self.__strip_completion(
            self.model.decode(result[initial_len - 1:])
        )

    def __get_arguments(
        self,
        prompt: str,
        function: Function
    ) -> List[Argument]:
        print("\n====================")
        print("====================\n")
        print(f"Generating arguments for prompt: {prompt}")
        print("\n====================")
        print("====================\n")
        arguments: List[Argument] = []
        prompt += "\nPick the parameters for this function:"
        prompt += f"{function.name}: {function.description}"
        prompt += '\n {"function": { "name": "'
        prompt += f'{function.name}", "parameters: [\n'
        for argument in function.arguments:
            end_tokens: set[int]
            valid_tokens: set[int]
            prompt += "\n{"
            prompt += f'"name": "{argument.name}",\n'
            prompt += f'"type": "{argument.type.value}",\n'
            prompt += '"value": '
            if argument.type == ArgumentType.STRING:
                prompt += '"'
                end_tokens = set(self.tokenizer.encode('"').tolist()[0])
                # Set valid_tokens to an empty set to allow any
                valid_tokens = set()
            elif argument.type == ArgumentType.BOOL:
                end_tokens = set(self.tokenizer.encode(' ').tolist()[0])
                end_tokens.update(self.tokenizer.encode('}').tolist()[0])
                end_tokens.update(self.tokenizer.encode(',').tolist()[0])
                valid_tokens = set(
                    self.tokenizer.encode('truefalse01').tolist()[0]
                )
            elif argument.type == ArgumentType.INT:
                end_tokens = set(self.tokenizer.encode(' ').tolist()[0])
                end_tokens.update(self.tokenizer.encode(',').tolist()[0])
                end_tokens.update(self.tokenizer.encode('}').tolist()[0])
                valid_tokens = set(
                    self.tokenizer.encode('0123456789').tolist()[0]
                )
            elif argument.type == ArgumentType.FLOAT:
                end_tokens = set(self.tokenizer.encode(' ').tolist()[0])
                end_tokens.update(self.tokenizer.encode('}').tolist()[0])
                end_tokens.update(self.tokenizer.encode(',').tolist()[0])
                valid_tokens = set(
                    self.tokenizer.encode('.0123456789').tolist()[0]
                )
            if len(valid_tokens):
                valid_tokens.update(end_tokens)
            result: List[int] = self.tokenizer.encode(prompt)[0].tolist()
            initial_len = len(prompt)
            print(prompt, end="")
            while (
                len(result) != initial_len
                and result[len(result) - 1] not in end_tokens
            ):
                logits = self.model.get_logits_from_input_ids(result)
                max_logit_index = logits.index(max(logits))
                while (
                    len(valid_tokens)
                    and max_logit_index not in valid_tokens
                ):
                    logits[max_logit_index] = -1
                    max_logit_index = logits.index(max(logits))
                result.append(max_logit_index)
                print(self.model.decode([max_logit_index]), end="")
            arguments.append(
                Argument(
                    name=argument.name,
                    type=argument.type,
                    value=self.model.decode(result[initial_len - 1:])
                )
            )
        return arguments

    def get_next_item(
        self,
        prompt: str,
        functions: List[Function]
    ) -> OutputItem:
        item: OutputItem = {"prompt": prompt, "name": "", "arguments": []}
        item["name"] = self.__get_name(prompt, functions)
        matching_functions = [
            function
            for function in functions
            if function.name == item["name"]
        ]
        if not len(matching_functions):
            raise GenerationError(f"Generated name {item["name"]} invalid.")
        function = matching_functions[0]
        arguments = self.__get_arguments(prompt, function)
        item["arguments"] = arguments
        print("\n====================")
        print("====================")
        print("Result:")
        print(item)
        print("====================")
        print("====================\n")
        return item
