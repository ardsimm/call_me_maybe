from typing import List, Optional
from src.models.function import Function, Parameter
from src.prompting.__templates import PromptingTemplates


class Prompting:
    """Builds the chat-template-style prompt strings fed to the model."""

    __context_prompt = """<|im_start|>system
You are an assistant for Python function calling.

Given a user request, select the appropriate function and determine the \
concrete values required for its parameters.
<|im_end|>"""

    @classmethod
    def build_name_generation_prompt(
        cls, user_prompt: str, functions: List[Function]
    ) -> str:
        """Build the prompt used to generate a function name.

        Parameters
        ----------
        user_prompt : str
            The user's natural-language request.
        functions : list of Function
            The functions the model may choose from.

        Returns
        -------
        str
            The full prompt, ready for tokenization.

        Raises
        ------
        GenerationError
            Forwarded from `PromptingTemplates.get_function_name_template`
            if the template files cannot be loaded.
        """
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
        """Build the prompt used to start generating `picked_function`'s
        parameters.

        Parameters
        ----------
        user_prompt : str
            The user's natural-language request.
        picked_function : Function
            The function whose parameters will be generated next.

        Returns
        -------
        str
            The full prompt, ready for tokenization.

        Raises
        ------
        GenerationError
            Forwarded from
            `PromptingTemplates.get_function_parameters_template` if the
            template files cannot be loaded.
        """
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
        """Append the next parameter's prompt section to `current_prompt`.

        Parameters
        ----------
        current_prompt : str
            The prompt built so far.
        function : Function
            The function whose parameter is being generated.
        next_parameter : Parameter
            The parameter to prompt for next.
        last_generated_parameter : Parameter or None
            The previously generated parameter, threaded in as context, if
            any.

        Returns
        -------
        str
            `current_prompt` with the next parameter's section appended.

        Raises
        ------
        GenerationError
            Forwarded from
            `PromptingTemplates.get_next_function_parameter_template` if
            the template files cannot be loaded.
        """
        return PromptingTemplates.get_next_function_parameter_template(
            current_prompt, function, next_parameter, last_generated_parameter
        )
