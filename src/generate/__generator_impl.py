from .generator import Generator
from ..models.function import Function
from typing import List
from ..models.output_item import OutputItem
from torch import Tensor


class GeneratorImpl(Generator):

    def __get_name(self, prompt: str, valid_names: List[str]) -> str:
        end_tokens: List[Tensor] = [
            self.tokenizer.encode('"'),
            self.tokenizer.encode('",'),
        ]
        prompt += '{ "name": "'
        result: List[int] = self.tokenizer.encode(prompt)[0].tolist()
        initial_len = len(result)
        logits: List[float]
        while result[len(result) - 1] not in end_tokens:
            logits = self.model.get_logits_from_input_ids(result)
            result.append(logits.index(max(logits)))
        return self.model.decode(result[: initial_len - 1])

    def __get_arguments(self, prompt: str, function: Function) -> List[str]:
        raise NotImplementedError("Method __get_arguments of GeneratorImpl" +
                                  " not yet implemented")

    def get_next_item(
        self, prompt: str, functions: List[Function]
    ) -> OutputItem:
        item: OutputItem = {"prompt": prompt, "fn_name": "", "arguments": []}
        item["fn_name"] = self.__get_name(
            prompt, [function.name for function in functions]
        )
        return item
