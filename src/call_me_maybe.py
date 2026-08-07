from src.generate import GeneratorFactory
from src.generate.generation_error import GenerationError
from src.parsing import ParserFactory, Parser
from src.models import Arguments, Context
import sys


class CallMeMaybe:
    @staticmethod
    def run() -> None:
        parser: Parser = ParserFactory.get_instance()
        arguments: Arguments = parser.parse(sys.argv[1:])
        context = Context(arguments)
        generator = GeneratorFactory.get_instance()
        for prompt in context.prompts:
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
            name = generator.generate_name(prompt, context.functions)
            print(f"Generated name: [{name}]")
            filtered_functions = [
                function
                for function in context.functions
                if function.name == name
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
