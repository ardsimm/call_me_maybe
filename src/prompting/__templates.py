from enum import StrEnum
import os
from typing import Dict, List, Optional
from src.models.function import Function, Parameter, ParameterType
from src.generate.generator_exceptions import GenerationError


class TemplateDirectories(StrEnum):
    FUNCTION_NAMES_PATH = ("data/templates/function_names",)
    FUNCTION_PARAMETERS_PATH = "data/templates/function_parameters"


class FunctionNamesTemplates(StrEnum):
    FUNCTION_NAME_MAIN = ("function_name_main_template.txt",)
    FUNCTION_NAME_OPTIONS = "function_name_option_template.txt"


class FunctionParametersTemplates(StrEnum):
    FUNCTION_PARAMETER_OPTION = "function_parameter_option_template.txt"
    FUNCTION_PARAMETERS_MAIN = "function_parameters_main_template.txt"
    GENERATED_PARAMETER_TEMPLATE = "generated_parameter_template.txt"
    UNGENERATED_PARAMETER_TEMPLATE = "ungenerated_parameter_template.txt"


class PromptingTemplates:

    __templates: Optional[Dict[str, str]] = None

    @classmethod
    def __load_templates(cls) -> None:
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
        function_name_main_template = cls.__get_templates().get(
            FunctionNamesTemplates.FUNCTION_NAME_MAIN
        )
        function_options_template = str(
            cls.__get_templates().get(
                FunctionNamesTemplates.FUNCTION_NAME_OPTIONS
            )
        )
        if (
            function_name_main_template is None
            or function_options_template is None
        ):
            raise GenerationError("Missing function names template")
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
        function_parameter_main_template = cls.__get_templates().get(
            FunctionParametersTemplates.FUNCTION_PARAMETERS_MAIN
        )
        function_parameter_option_template = cls.__get_templates().get(
            FunctionParametersTemplates.FUNCTION_PARAMETER_OPTION
        )
        if (
            function_parameter_main_template is None
            or function_parameter_option_template is None
        ):
            raise GenerationError("Missing function parameters template")
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
        generated_parameter_template = cls.__get_templates().get(
            FunctionParametersTemplates.GENERATED_PARAMETER_TEMPLATE
        )
        ungenerated_parameter_template = cls.__get_templates().get(
                    FunctionParametersTemplates.UNGENERATED_PARAMETER_TEMPLATE
                )
        if (
            generated_parameter_template is None
            or ungenerated_parameter_template is None
        ):
            raise GenerationError("Missing function parameter template")
        if generated_parameter is not None:
            assert generated_parameter.value is not None
            current_prompt += (
                generated_parameter_template
                .replace("{[PARAMETER_VALUE]}", generated_parameter.value)
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
