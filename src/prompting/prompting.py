from typing import List, Optional
from src.models.function import Function, Parameter
from src.prompting.__templates import PromptingTemplates


class Prompting:

    __context_prompt = """<|im_start|>system
You are an assistant for Python function calling.

Given a user request, select the appropriate function and determine the \
concrete values required for its parameters.
<|im_end|>"""

    @classmethod
    def build_name_generation_prompt(
        cls, user_prompt: str, functions: List[Function]
    ) -> str:
        return "\n\n".join(
            [
                cls.__context_prompt,
                PromptingTemplates.get_function_name_template(
                    user_prompt, functions
                ),
            ]
        )

    @classmethod
    def build_parameter_generation_prompt(
        cls,
        user_prompt: str,
        picked_function: Function,
    ) -> str:
        return "\n\n".join(
            [
                cls.__context_prompt,
                PromptingTemplates.get_function_parameters_template(
                    user_prompt, picked_function
                ),
            ]
        )

    @classmethod
    def build_next_parameter_generation_prompt(
        cls,
        current_prompt: str,
        function: Function,
        next_parameter: Parameter,
        last_generated_parameter: Optional[Parameter] = None,
    ) -> str:
        return PromptingTemplates.get_next_function_parameter_template(
            current_prompt, function, next_parameter, last_generated_parameter
        )
