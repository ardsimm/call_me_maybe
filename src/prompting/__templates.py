from enum import StrEnum
import os
from typing import Dict, List, Optional
from src.models.function import Function, Parameter, ParameterType
from src.generate.generator_exceptions import GenerationError


class TemplateDirectories(StrEnum):
    """Directories holding the raw prompt template `.txt` files."""

    FUNCTION_NAMES_PATH = ("data/templates/function_names",)
    FUNCTION_PARAMETERS_PATH = "data/templates/function_parameters"


class FunctionNamesTemplates(StrEnum):
    """Filenames of the function-name-selection prompt templates."""

    FUNCTION_NAME_MAIN = ("function_name_main_template.txt",)
    FUNCTION_NAME_OPTIONS = "function_name_option_template.txt"


class FunctionParametersTemplates(StrEnum):
    """Filenames of the function-parameter-generation prompt templates."""

    FUNCTION_PARAMETER_OPTION = "function_parameter_option_template.txt"
    FUNCTION_PARAMETERS_MAIN = "function_parameters_main_template.txt"
    GENERATED_PARAMETER_TEMPLATE = "generated_parameter_template.txt"
    UNGENERATED_PARAMETER_TEMPLATE = "ungenerated_parameter_template.txt"


class PromptingTemplates:
    """Builds prompt strings by filling in cached template files.

    Templates are plain text files containing `{[PLACEHOLDER]}` markers,
    lazily loaded once into `__templates` on first use and reused for
    every subsequent prompt.
    """

    __templates: Optional[Dict[str, str]] = None

    @classmethod
    def __load_templates(cls) -> None:
        """Read every template file into `__templates`, keyed by filename.

        Raises
        ------
        IOError
            If any template file under `TemplateDirectories` cannot be
            opened or read.
        """
        cls.__templates = {}
        for function_name_template in FunctionNamesTemplates:
            with open(
                os.path.join(
                    TemplateDirectories.FUNCTION_NAMES_PATH,
                    function_name_template.value,
                )
            ) as template_file:
                cls.__templates[function_name_template.value] = (
                    template_file.read()
                )

        for function_parameter_template in FunctionParametersTemplates:
            with open(
                os.path.join(
                    TemplateDirectories.FUNCTION_PARAMETERS_PATH,
                    function_parameter_template.value,
                )
            ) as template_file:
                cls.__templates[function_parameter_template.value] = (
                    template_file.read()
                )

    @classmethod
    def __get_templates(cls) -> Dict[str, str]:
        """Return the cached templates, loading them on first call.

        Returns
        -------
        dict of str to str
            Every template's contents, keyed by filename.

        Raises
        ------
        GenerationError
            Wrapping an `IOError` from `__load_templates` if a template
            file cannot be read.
        """
        if cls.__templates is None:
            try:
                cls.__load_templates()
            except IOError as e:
                raise GenerationError(
                    f"Failed to load prompt template files: {e}"
                )
        assert cls.__templates is not None
        return cls.__templates

    @classmethod
    def get_function_name_template(
        cls, user_prompt: str, functions: List[Function]
    ) -> str:
        """Build the prompt asking the model to choose a function name.

        Parameters
        ----------
        user_prompt : str
            The user's natural-language request.
        functions : list of Function
            Every candidate function, each rendered as one option in the
            prompt.

        Returns
        -------
        str
            The filled-in function-name-selection prompt.

        Raises
        ------
        GenerationError
            Forwarded from `__get_templates` if a template file cannot
            be read.
        """
        function_name_main_template = str(
            cls.__get_templates().get(
                FunctionNamesTemplates.FUNCTION_NAME_MAIN
            )
        )
        function_options_template = str(
            cls.__get_templates().get(
                FunctionNamesTemplates.FUNCTION_NAME_OPTIONS
            )
        )
        function_options: str = "\n".join(
            [
                function_options_template.replace(
                    "{[FUNCTION_NAME]}", function.name
                ).replace("{[FUNCTION_DESCRIPTION]}", function.description)
                for function in functions
            ]
        )
        return function_name_main_template.replace(
            "{[FUNCTION_OPTIONS]}", function_options
        ).replace("{[USER_PROMPT]}", user_prompt)

    @classmethod
    def get_function_parameters_template(
        cls, user_prompt: str, function: Function
    ) -> str:
        """Build the prompt introducing `function`'s parameters.

        Parameters
        ----------
        user_prompt : str
            The user's natural-language request.
        function : Function
            The function whose parameters are about to be generated,
            each rendered as one option in the prompt.

        Returns
        -------
        str
            The filled-in function-parameters prompt.

        Raises
        ------
        GenerationError
            Forwarded from `__get_templates` if a template file cannot
            be read.
        """
        function_parameter_main_template = str(
            cls.__get_templates().get(
                FunctionParametersTemplates.FUNCTION_PARAMETERS_MAIN
            )
        )
        function_parameter_option_template = str(
            cls.__get_templates().get(
                FunctionParametersTemplates.FUNCTION_PARAMETER_OPTION
            )
        )
        parameter_options = "\n".join(
            [
                function_parameter_option_template.replace(
                    "{[PARAMETER_NAME]}", parameter.name
                ).replace(
                    "{[PARAMETER_TYPE]}",
                    (
                        parameter.type.value
                        if parameter.type != ParameterType.FLOAT
                        else "float"
                    ),
                )
                for parameter in function.parameters
            ]
        )
        return (
            function_parameter_main_template.replace(
                "{[USER_PROMPT]}", user_prompt
            )
            .replace("{[FUNCTION_NAME]}", function.name)
            .replace("{[FUNCTION_DESCRIPTION]}", function.description)
            .replace("{[FUNCTION_PARAMETERS]}", parameter_options)
        )

    @classmethod
    def get_next_function_parameter_template(
        cls,
        current_prompt: str,
        function: Function,
        next_parameter: Parameter,
        generated_parameter: Optional[Parameter] = None,
    ) -> str:
        """Append the previous parameter's value and prompt for the next.

        If `generated_parameter` was already generated (i.e. not `None`
        and its `value` is set), its value is appended to `current_prompt`
        first, so each parameter's prompt carries every prior parameter's
        generated value as context. Then a request for `next_parameter`
        is appended.

        Parameters
        ----------
        current_prompt : str
            The prompt built so far.
        function : Function
            The function whose parameters are being generated.
        next_parameter : Parameter
            The parameter to prompt for next.
        generated_parameter : Parameter, optional
            The most recently generated parameter, if any, appended to
            `current_prompt` before the next request.

        Returns
        -------
        str
            The extended prompt, ready for `next_parameter`'s generation.

        Raises
        ------
        GenerationError
            Forwarded from `__get_templates` if a template file cannot
            be read.
        """
        generated_parameter_template = str(
            cls.__get_templates().get(
                FunctionParametersTemplates.GENERATED_PARAMETER_TEMPLATE
            )
        )
        ungenerated_parameter_template = str(
            cls.__get_templates().get(
                FunctionParametersTemplates.UNGENERATED_PARAMETER_TEMPLATE
            )
        )
        if (
            generated_parameter is not None
            and generated_parameter.value is not None
        ):
            current_prompt += (
                generated_parameter_template.replace(
                    "{[PARAMETER_VALUE]}", generated_parameter.value
                )
                + "\n"
            )
        return (
            (current_prompt + ungenerated_parameter_template)
            .replace("{[PARAMETER_NAME]}", next_parameter.name)
            .replace(
                "{[PARAMETER_TYPE]}",
                (
                    next_parameter.type.value
                    if next_parameter.type != ParameterType.FLOAT
                    else "float"
                ),
            )
            .replace("{[FUNCTION_NAME]}", function.name)
        )
