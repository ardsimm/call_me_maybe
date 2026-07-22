from src.models.function import Argument, ArgumentType
from src.parsing import ParserFactory, Parser
from src.generate import GeneratorFactory, Generator
from src.models import Arguments, Function
import sys
from traceback import print_exception


def main() -> None:
    parser: Parser = ParserFactory.get_instance()
    generator: Generator = GeneratorFactory.get_instance()
    arguments: Arguments = parser.parse(sys.argv[1:])
    arguments = arguments
    # print(
    generator.get_next_item(
        prompt="What is the sum of 2 and 4 ?",
        functions=[
            Function(
                name="fn_add",
                description="Add two integers",
                arguments=[
                    Argument(name="a", type=ArgumentType.FLOAT),
                    Argument(name="b", type=ArgumentType.FLOAT)
                ],
            ),
            Function(
                name="fn_greet",
                description="Greet someone",
                arguments=[
                    Argument(name="name", type=ArgumentType.STRING)
                ],
            ),
        ],
    ),
    generator.get_next_item(
        prompt="Can greet my mom ? Her name is Pervenche.",
        functions=[
            Function(
                name="fn_add",
                description="Add two integers",
                arguments=[Argument(name="a", type=ArgumentType.INT)],
            ),
            Function(
                name="fn_greet",
                description="Greet someone",
                arguments=[
                    Argument(name="name", type=ArgumentType.STRING)
                ],
            ),
        ],
    )
    print(generator.model.get_path_to_vocab_file())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("An unhandled error occured:\n", file=sys.stderr)
        print_exception(e)
