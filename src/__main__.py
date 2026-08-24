from src.call_me_maybe import CallMeMaybe
import sys
from traceback import print_exception


def main() -> None:
    CallMeMaybe.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("An unhandled error occured:\n", file=sys.stderr)
        print_exception(e)
        sys.exit(1)
