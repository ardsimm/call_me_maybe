from src.generate import GeneratorFactory
from src.generate import GenerationError
from src.parsing import ParserFactory
from src.models import Arguments, Context, OutputItem, ParameterType
from src.adapter import AdapterFactory, AdapterType, SerializationException
from src.parsing import ParsingError, ParsingValidationError
from typing import List, Union
import sys
from pathlib import Path


header = r"""           _ _                                              _
  ___ __ _| | |    _ __ ___   ___     _ __ ___   __ _ _   _| |__   ___
 / __/ _` | | |   | '_ ` _ \ / _ \   | '_ ` _ \ / _` | | | | '_ \ / _ \
| (_| (_| | | |   | | | | | |  __/   | | | | | | (_| | |_| | |_) |  __/
 \___\__,_|_|_|___|_| |_| |_|\___|___|_| |_| |_|\__,_|\__, |_.__/ \___|
             |_____|            |_____|               |___/

Made with love and pain by ardsimm
"""


class CallMeMaybe:

    @staticmethod
    def __get_arguments() -> Arguments:
        parser = ParserFactory.get_instance()
        return parser.parse(sys.argv[1:])

    @staticmethod
    def __get_context(arguments: Arguments) -> Context:
        return Context(arguments)

    @staticmethod
    def __process_prompt(prompt: str, context: Context) -> OutputItem:
        generator = GeneratorFactory.get_instance()
        item: OutputItem = {"prompt": "", "name": "", "parameters": {}}
        item["prompt"] = prompt

        print(
            "\n=====================================================",
            "=====================================================",
            f"Generating for prompt: {prompt}",
            "=====================================================",
            "=====================================================",
            sep="\n",
        )

        name = generator.generate_name(prompt, context.functions)

        filtered_functions = [
            function for function in context.functions if function.name == name
        ]
        if not len(filtered_functions):
            raise GenerationError(f"Invalid function name: [{name}]")
        print(f"Generated name: [{name}]")

        picked_function = filtered_functions[0]
        item["name"] = picked_function.name
        parameters = generator.generate_parameters(prompt, picked_function)
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
                if parameter.value.lower() == "true":
                    parsed_parameter = True
                elif parameter.value.lower() == "false":
                    parsed_parameter = False
                else:
                    raise ValueError(f"Invalid bool value {parameter.value}")
            else:
                parsed_parameter = parameter.value
            item["parameters"][parameter.name] = parsed_parameter
        return item

    @classmethod
    def __process_prompts(cls, context: Context) -> List[OutputItem]:
        items: List[OutputItem] = []

        for prompt in context.prompts:
            try:
                items.append(cls.__process_prompt(prompt, context))
            except GenerationError as err:
                print(f"Error while generating prompt {prompt}:\n{err}")
                items.append({"prompt": "", "name": "", "parameters": {}})
                continue
        return items

    @staticmethod
    def __write_output(items: List[OutputItem], arguments: Arguments) -> None:
        adapter = AdapterFactory.get_instance(AdapterType.JSON)
        print("\nWriting result to output file...")
        serialized = adapter.serialize(items)
        output_file_path = Path(arguments.output)
        output_file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(
            output_file_path, mode="w"
        ) as output_file:
            output_file.write(serialized)

    @classmethod
    def run(cls) -> None:
        print(header)
        try:
            arguments: Arguments = cls.__get_arguments()
            context = cls.__get_context(arguments)
        except (ParsingValidationError, ParsingError) as e:
            print(f"Parsing failed: {e}")
            return
        items: List[OutputItem] = cls.__process_prompts(context)
        try:
            cls.__write_output(items, arguments)
        except SerializationException as e:
            print(f"Failed to serialize result: {e}")
            return
        except IOError as e:
            print(f"Failed to write output file: {e}")
            return
        print("\nDone ! :3")
