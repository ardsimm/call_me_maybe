import math

from src.generate import GeneratorFactory
from src.generate import GenerationError
from src.model.model import Model
from src.parsing import ParserFactory
from src.models import Arguments, Context, OutputItem, ParameterType
from src.adapter import AdapterFactory, AdapterType, SerializationException
from src.parsing import ParsingError, ParsingValidationError
from typing import List, Union
import sys
from pathlib import Path

HEADER = r"""           _ _                                              _
  ___ __ _| | |    _ __ ___   ___     _ __ ___   __ _ _   _| |__   ___
 / __/ _` | | |   | '_ ` _ \ / _ \   | '_ ` _ \ / _` | | | | '_ \ / _ \
| (_| (_| | | |   | | | | | |  __/   | | | | | | (_| | |_| | |_) |  __/
 \___\__,_|_|_|___|_| |_| |_|\___|___|_| |_| |_|\__,_|\__, |_.__/ \___|
             |_____|            |_____|               |___/

Made with love and pain by ardsimm
"""


MAX_LOG_SEPARATOR_LEN = len(HEADER.split("\n")[1]) + 1


class CallMeMaybe:

    @staticmethod
    def __strip_trailing_minus_sign(s: str) -> str:
        # In specific cases, the LLM might generate the token `-"` or `-",`
        # at the end of an number. With our logic loading every token
        # containing unescaped quotes and using them as end
        # sequences for our completion and since we strip the quotes after
        # decoding, keeping the first non-quote character without any constrain
        # we can get invalid numbers such as `-42-`.
        # For instance:
        # User: `Print the number "-42-4"``
        # LLM: `-42-"`,
        # After quotes stripping: number = `-42-`
        # The following function is a workaround for this bug,
        s_len = len(s)
        while s.endswith("-"):
            s = s[:s_len - 1]
            s_len -= 1
        return s

    @staticmethod
    def __get_arguments() -> Arguments:
        parser = ParserFactory.get_instance()
        return parser.parse(sys.argv[1:])

    @staticmethod
    def __get_context(arguments: Arguments) -> Context:
        return Context(arguments)

    @classmethod
    def __process_prompt(cls, prompt: str, context: Context) -> OutputItem:
        generator = GeneratorFactory.get_instance()
        item: OutputItem = {"prompt": "", "name": "", "parameters": {}}
        item["prompt"] = prompt
        print(
            "\n" + "=" * min(len(prompt), MAX_LOG_SEPARATOR_LEN),
            "=" * min(len(prompt), MAX_LOG_SEPARATOR_LEN),
            prompt,
            "=" * min(len(prompt), MAX_LOG_SEPARATOR_LEN),
            "=" * min(len(prompt), MAX_LOG_SEPARATOR_LEN),
            sep="\n",
        )
        if "<|im_end|>" in prompt or "<|im_start|>" in prompt:
            print("Nice try, not computing this one :p")
            return {"prompt": prompt, "name": "", "parameters": {}}

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
        for parameter in parameters:
            parsed_parameter: Union[int, float, str, bool]
            assert parameter.value is not None
            if parameter.type == ParameterType.INT:
                try:
                    parameter.value = cls.__strip_trailing_minus_sign(
                        parameter.value
                    )
                    parsed_parameter = int(parameter.value)
                    if math.isinf(parsed_parameter):
                        raise ValueError("Int parameter overflowed")
                except ValueError as err:
                    print(
                        f"Failed to generate int parameter {parameter.name}:",
                        err.__str__(),
                    )
                    parsed_parameter = 42

            elif parameter.type == ParameterType.FLOAT:
                try:
                    parameter.value = cls.__strip_trailing_minus_sign(
                        parameter.value
                    )
                    parsed_parameter = float(parameter.value)
                    if math.isinf(parsed_parameter):
                        raise ValueError("Float parameter overflowed")
                except ValueError as err:
                    print(f"Failed to generate float parameter {
                            parameter.name
                        }:", err.__str__())
                    parsed_parameter = 42.0

            elif parameter.type == ParameterType.BOOL:
                if parameter.value.lower() == "true" or parameter.value == "1":
                    parsed_parameter = True
                elif (
                    parameter.value.lower() == "false"
                    or parameter.value == "0"
                ):
                    parsed_parameter = False
                else:
                    print(
                        f"Failed to generate parameter {parameter.name}:",
                        f"Invalid boolean value :{parameter.value}",
                    )
                    parsed_parameter = ""

            else:
                parsed_parameter = parameter.value

            item["parameters"][parameter.name] = parsed_parameter

        print("Generated parameters:")
        for parameter in parameters:
            print(
                f"- {parameter.name} <{parameter.type.value}>:",
                f"[{item["parameters"][parameter.name]}]",
            )

        return item

    @classmethod
    def __process_prompts(cls, context: Context) -> List[OutputItem]:
        items: List[OutputItem] = []

        for prompt in context.prompts:
            item: OutputItem = {"prompt": prompt, "name": "", "parameters": {}}
            try:
                item = cls.__process_prompt(prompt, context)
                items.append(item)
            except GenerationError as err:
                print(f"Error while generating prompt {prompt}:\n{err}")
                items.append(item)
                continue
        return items

    @staticmethod
    def __write_output(items: List[OutputItem], arguments: Arguments) -> None:
        adapter = AdapterFactory.get_instance(AdapterType.JSON)
        print("\nWriting result to output file...")
        serialized = adapter.serialize(items)
        output_file_path = Path(arguments.output)
        output_file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(output_file_path, mode="w") as output_file:
            output_file.write(serialized)

    @classmethod
    def run(cls) -> None:
        print(HEADER)
        try:
            arguments: Arguments = cls.__get_arguments()
            context = cls.__get_context(arguments)
        except (ParsingValidationError, ParsingError) as e:
            print(f"Parsing failed: {e}")
            return
        if not len(context.prompts):
            print("The prompts file was valid json but was empty, exiting.")
            return
        # Pre-load model weigths
        Model.get_instance()
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
