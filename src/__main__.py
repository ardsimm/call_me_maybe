from src.parsing.parser_factory import ParserFactory
import sys


def main() -> None:
    parser = ParserFactory.get_instance()
    arguments = parser.parse(sys.argv[1:])
    print("Parser output: ", arguments)


if __name__ == "__main__":
    main()
