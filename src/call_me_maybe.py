from src.generate import GeneratorFactory
from src.generate import GenerationError
from src.parsing import ParserFactory, Parser
from src.models import Arguments, Context, OutputItem, ParameterType
from src.adapter import AdapterFactory, AdapterType, SerializationException
from src.parsing import ParsingError, ParsingValidationError
from typing import List, Union
import sys
import os


class CallMeMaybe:
    @staticmethod
    def run() -> None:
        parser: Parser = ParserFactory.get_instance()
        try:
            arguments: Arguments = parser.parse(sys.argv[1:])
        except (ParsingValidationError, ParsingError):
            print("Parsing failed")
            return
        context = Context(arguments)
        generator = GeneratorFactory.get_instance()
        items: List[OutputItem] = []
        for prompt in context.prompts:
            item: OutputItem = {"prompt": "", "name": "", "parameters": {}}
            item["prompt"] = prompt
            print(
                "=====================================================",
                "=====================================================",
                f"Generating for prompt: {prompt}",
                "=====================================================",
                "=====================================================",
                sep="\n",
            )
            try:
                name = generator.generate_name(prompt, context.functions)
                filtered_functions = [
                    function
                    for function in context.functions
                    if function.name == name
                ]
                if not len(filtered_functions):
                    raise GenerationError(f"Invalid function name: [{name}]")
            except GenerationError:
                print("Name generation failed. continuing...")
                items.append(item)
                continue
            print(f"Generated name: [{name}]")
            picked_function = filtered_functions[0]
            item["name"] = picked_function.name
            try:
                parameters = generator.generate_parameters(
                    prompt, picked_function
                )
            except GenerationError:
                print("Parameters generation failed. continuing...")
                items.append(item)
                continue
            print("Generated parameters:")
            for parameter in parameters:
                print(
                    f"- {parameter.name} <{parameter.type.value}>:",
                    f"[{parameter.value}]",
                )
                parsed_parameter: Union[int, float, str, bool]
                assert parameter.value is not None
                if parameter.type == ParameterType.INT:
                    parsed_parameter = int(parameter.value)
                elif parameter.type == ParameterType.FLOAT:
                    parsed_parameter = float(parameter.value)
                elif parameter.type == ParameterType.BOOL:
                    parsed_parameter = bool(parameter.value)
                else:
                    parsed_parameter = parameter.value
                item["parameters"][parameter.name] = parsed_parameter
                items.append(item)
        adapter = AdapterFactory.get_instance(AdapterType.JSON)
        print("Writing result to output file...")
        try:
            serialized = adapter.serialize(items)
        except SerializationException:
            print("Result serialization failed...")
            return
        os.makedirs("data/output", exist_ok=True)
        output_file_path = os.path.join("/data/output", arguments.output)
        try:
            with open(
                output_file_path, mode="w"
            ) as output_file:
                output_file.write(serialized)
        except IOError:
            print("Failed to write output file.")
            return
        print("Done ! :3")
