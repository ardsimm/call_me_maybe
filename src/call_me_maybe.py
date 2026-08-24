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


LOG_SEPARATOR_LEN = len(HEADER.split("\n")[1]) + 1


class CallMeMaybe:
    """Entry point orchestrating the full prompt-to-function-call pipeline.

    Parses CLI arguments, loads/validates the functions definition and
    prompts, generates a name and parameters per prompt, coerces each
    parameter to its declared type, and writes every result out as JSON.
    """

    @staticmethod
    def __strip_number(s: str) -> str:
        """Trim trailing non-digit characters merged into a number token.

        In specific cases, the LLM might generate the token `-"` or `-",`
        at the end of a number. Because every vocab token containing an
        unescaped quote is used as a completion end sequence, and only
        the text before that quote is kept, a merged token can leave
        trailing garbage after the last digit, producing an invalid
        number such as `-42-`. For example, given the prompt
        `Print the number "-42-4"`, the model may generate `-42-"`;
        after stripping the quote the value is `-42-`. This function
        trims trailing non-digit characters off such a value.

        Parameters
        ----------
        s : str
            The raw parameter text, straight out of generation.

        Returns
        -------
        str
            `s` with any trailing non-digit characters removed. Returns
            `""` if `s` contains no digit at all.
        """
        s_len = len(s)
        while (
            not s.endswith(
                (
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                )
            )
            and s_len > 0
        ):
            s = s[: s_len - 1]
            s_len -= 1
        return s

    @staticmethod
    def __get_arguments() -> Arguments:
        """Parse `sys.argv` into a validated `Arguments`.

        Returns
        -------
        Arguments
            The parsed and validated CLI arguments.

        Raises
        ------
        ParsingError
            Forwarded from `Parser.parse` if an input file cannot be
            opened or is not valid JSON.
        ParsingValidationError
            Forwarded from `Parser.parse` if the parsed arguments fail
            pydantic validation.
        """
        parser = ParserFactory.get_instance()
        return parser.parse(sys.argv[1:])

    @staticmethod
    def __get_context(arguments: Arguments) -> Context:
        """Build the run `Context` from `arguments`.

        Parameters
        ----------
        arguments : Arguments
            The parsed CLI arguments naming the functions-definition and
            prompts files.

        Returns
        -------
        Context
            The loaded functions and prompts.

        Raises
        ------
        ParsingError
            Forwarded from `Context.__init__` if a file cannot be opened,
            is not valid JSON, or its content does not match the expected
            shape.
        """
        return Context(arguments)

    @classmethod
    def __process_prompt(cls, prompt: str, context: Context) -> OutputItem:
        """Generate a function call for a single `prompt`.

        Guards against prompt injection by refusing any prompt containing
        `<|im_end|>` or `<|im_start|>` (the chat template's special
        tokens) outright, returning an empty `OutputItem` for it instead
        of generating. Otherwise generates a name, resolves it against
        `context.functions`, generates its parameters, and coerces each
        parameter's raw string value to its declared `ParameterType`
        (`INT`/`FLOAT` values that fail to parse or overflow to infinity
        fall back to `42`/`42.0`; an unrecognized `BOOL` value falls back
        to `""`).

        Parameters
        ----------
        prompt : str
            The user's natural-language request.
        context : Context
            The loaded functions and prompts for this run.

        Returns
        -------
        OutputItem
            The prompt, chosen function name, and coerced parameters.

        Raises
        ------
        GenerationError
            If the generated name matches none of `context.functions`, or
            forwarded from `Generator.generate_name`/`generate_parameters`.
        ValueError
            Forwarded from `Generator.generate_name`/`generate_parameters`.
        """
        generator = GeneratorFactory.get_instance()
        item: OutputItem = {"prompt": "", "name": "", "parameters": {}}
        item["prompt"] = prompt
        print(
            "\n" + "=" * LOG_SEPARATOR_LEN,
            "=" * LOG_SEPARATOR_LEN,
            prompt,
            "=" * LOG_SEPARATOR_LEN,
            "=" * LOG_SEPARATOR_LEN,
            sep="\n",
        )
        if "<|im_end|>" in prompt or "<|im_start|>" in prompt:
            # This.. this is proper anti prompt injection code right there
            # OpenAI aint got nothing on me
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
                    parameter.value = cls.__strip_number(parameter.value)
                    parsed_parameter = int(parameter.value)
                    if math.isinf(parsed_parameter):
                        # Python is a FAKE language made by CRAZY people
                        raise ValueError("Int parameter overflowed")
                except ValueError as err:
                    print(
                        f"Failed to generate int parameter {parameter.name}:",
                        err.__str__(),
                    )
                    parsed_parameter = 42

            elif parameter.type == ParameterType.FLOAT:
                try:
                    parameter.value = cls.__strip_number(parameter.value)
                    parsed_parameter = float(parameter.value)
                    if math.isinf(parsed_parameter):
                        # Python is a FAKE language made by CRAZY people
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
        """Generate a function call for every prompt in `context`.

        A `GenerationError` from any single prompt is caught and logged
        so one bad prompt does not abort the whole batch; that prompt's
        `OutputItem` is appended with an empty name and parameters.

        Parameters
        ----------
        context : Context
            The loaded functions and prompts for this run.

        Returns
        -------
        list of OutputItem
            One item per prompt in `context.prompts`, in order.
        """
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
        """Serialize `items` to JSON and write them to `arguments.output`.

        Creates any missing parent directories of the output path.

        Parameters
        ----------
        items : list of OutputItem
            The results to write out.
        arguments : Arguments
            Carries the output file path.

        Raises
        ------
        SerializationException
            Forwarded from `JSONAdapter.serialize` if `items` is not
            JSON-serializable.
        OSError
            If the output file or its parent directories cannot be
            created or written.
        """
        adapter = AdapterFactory.get_instance(AdapterType.JSON)
        print("\nWriting result to output file...")
        serialized = adapter.serialize(items)
        output_file_path = Path(arguments.output)
        output_file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(output_file_path, mode="w") as output_file:
            output_file.write(serialized)

    @classmethod
    def run(cls) -> None:
        """Run the full pipeline: parse args, generate, write output.

        Parsing/validation failures, an empty prompts file,
        serialization failures, and output write failures are all caught
        and logged here, returning early instead of propagating -- only
        a `GenerationError` from an individual prompt's own failure is
        handled earlier, in `__process_prompts`.

        Raises
        ------
        Exception
            Anything not explicitly caught above propagates uncaught to
            `__main__`, which prints a traceback and exits with status 1.
        """
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
