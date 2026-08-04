from typing import List

from src.generate import Generator, GeneratorFactory
from src.generate.generation_error import GenerationError
from src.models.function import Function, Parameter, ParameterType


class CallMeMaybe:
    @staticmethod
    def run() -> None:
        prompts = [
            "What is the sum of 2 and 4 ?",
            "Can you greet my mom ? Her name is Pervenche.",
            "Can you greet my mom ?"
        ]
        functions: List[Function] = [
            Function(
                name="fn_add",
                description="Add two integers",
                parameters=[
                    Parameter(name="a", type=ParameterType.FLOAT),
                    Parameter(name="b", type=ParameterType.FLOAT),
                ],
            ),
            Function(
                name="fn_greet",
                description="Greet someone",
                parameters=[Parameter(name="name", type=ParameterType.STRING)],
            ),
        ]
        generator: Generator = GeneratorFactory.get_instance()

        for prompt in prompts:
            print(
                "=====================================================",
                "=====================================================",
                sep="\n",
            )
            print("Generating for prompt:", prompt)
            print(
                "=====================================================",
                "=====================================================",
                sep="\n",
            )
            name = generator.generate_name(prompt, functions)
            print(f"Generated name: [{name}]")
            filtered_functions = [
                function for function in functions if function.name == name
            ]
            if not len(filtered_functions):
                raise GenerationError(f"Invalid function name: [{name}]")
            picked_function = filtered_functions[0]
            parameters = generator.generate_parameters(prompt, picked_function)
            print("Generated parameters:")
            for parameter in parameters:
                print(
                    f"- {parameter.name} <{parameter.type.value}>:",
                    f"[{parameter.value}]",
                )
