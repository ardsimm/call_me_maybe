from .generator import Generator
from ..models.function import Function
from typing import List
from ..models.output_item import OutputItem
from functools import reduce


class GeneratorImpl(Generator):

    def __strip_completion(
        self,
        completion: str
    ) -> str:
        name_length = len(completion)
        while completion.endswith((",", '"', "'", " ")):
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
        end_tokens: List[int] = self.tokenizer.encode('"').tolist()[0]

        prompt += "\nPick the function to run from the following options:\n"
        prompt += "\n".join([
            f"{function.name}: {function.description}"
            for function in functions
        ])
        prompt += '\n {"function": { "name": "'

        print("Prompting for name with prompt:", prompt, end="")

        result: List[int] = self.tokenizer.encode(
            prompt + f"\n{prompt}"
        )[0].tolist()

        initial_len = len(result)
        logits: List[float]

        encoded_names = [
            self.model.encode(function.name).tolist()[0]
            for function in functions
        ]
        reduced_name_tokens = reduce(
            lambda acc, el: acc + el,
            encoded_names,
            []
        )
        valid_tokens = set(reduced_name_tokens)
        valid_tokens.update(end_tokens)

        while result[len(result) - 1] not in end_tokens:
            logits = self.model.get_logits_from_input_ids(result)
            max_logit_index = logits.index(max(logits))
            while max_logit_index not in valid_tokens:
                logits[max_logit_index] = -1
                max_logit_index = logits.index(max(logits))
            print(self.model.decode([max_logit_index]), end="")
            result.append(max_logit_index)
        print("\n")
        return self.__strip_completion(
            self.model.decode(result[initial_len - 1:])
        )

    def __get_arguments(
        self,
        prompt: str,
        function: Function
    ) -> List[str]:
        raise NotImplementedError(
            "Method __get_arguments of GeneratorImpl" + " not yet implemented"
        )

    def get_next_item(
        self, prompt: str, functions: List[Function]
    ) -> OutputItem:
        item: OutputItem = {"prompt": prompt, "name": "", "arguments": []}
        item["name"] = self.__get_name(prompt, functions)
        return item
