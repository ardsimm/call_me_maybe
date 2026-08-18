from typing import List, Optional
from src.models.function import Function, Parameter, ParameterType


class Prompting:

    __context_prompt = """
<|im_start|>system
You are an assistant capable to execute python functions.
Your role, given a user prompt, will be to pick the functions to execute and
the values to pass as parameters.<|im_end|>
    """

    @classmethod
    def build_name_generation_prompt(
        cls,
        user_prompt: str,
        functions: List[Function]
    ) -> str:
        return (
            f"{cls.__context_prompt}\n\n"
            + "<|im_start|>system\n"
            + "You have access to the following functions:\n"
            + f"{"\n".join([
                f' - {function.name}: {function.description}'
                for function in functions
            ])}\n"
            + "Pick the appopriate function for the following user prompt."
            + "<|im_end|>\n"
            + f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
            + "<|im_start|>assistant\n"
            + '{"function": { "name": "'
        )

    @classmethod
    def build_parameter_generation_prompt(
        cls,
        user_prompt: str,
        picked_function: Function,
    ) -> str:
        prompt = (
            f"{cls.__context_prompt}\n\n"
            + f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
            + "<|im_start|>assistant\n"
            + '{"function": { "name": "'
            + f"{picked_function.name}\",<|im_end|>\n"
            + "<|im_start|>system\n"
            + "This function takes the following parameters:\n"
            + "\n".join([
                f"- {parameter.name}: {
                    parameter.type.value
                    if parameter.type != ParameterType.FLOAT
                    else 'float'
                }"
                for parameter in picked_function.parameters
            ])
            + "\n\nPick the values to pass as parameters<|im_end|>\n"
            + "<|im_start|>assistant\n"
            + '"parameters": [\n'
        )
        parameter_to_generate: Parameter = picked_function.parameters[0]
        i = 1
        parameters_len = len(picked_function.parameters)
        while (
            parameter_to_generate.value is not None
            and i < parameters_len
        ):
            prompt += (
                "\t{\n\t\t"
                + f"\"{parameter_to_generate.name}\": {
                    f"\"{parameter_to_generate.value}\""
                    if parameter_to_generate.type == ParameterType.STRING
                    else parameter_to_generate.value
                }"
                + "\n\t},\n"
            )
            parameter_to_generate = picked_function.parameters[i]
            i += 1
        prompt += (
            "\t{\n\t\t" + f'"{parameter_to_generate.name}: "'
        )
        return prompt
