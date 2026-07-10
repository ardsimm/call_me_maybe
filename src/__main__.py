from src.parsing.parser_factory import ParserFactory
import sys


def main() -> None:
    parser = ParserFactory.get_instance()
    arguments = parser.parse(sys.argv[1:])
    print("Parser output: ", arguments)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unhandled error occured:\n{e}", file=sys.stderr)
