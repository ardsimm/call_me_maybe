from src.call_me_maybe import CallMeMaybe
import sys
from traceback import print_exception


def main() -> None:
    """Run the program.

    Raises
    ------
    Exception
        Anything `CallMeMaybe.run` does not catch itself (see its
        docstring) propagates uncaught. The `except Exception` guard
        below only prints a traceback to stderr -- it never calls
        `sys.exit(1)`, so the process still exits 0 even after a crash.
    """
    CallMeMaybe.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("An unhandled error occured:\n", file=sys.stderr)
        print_exception(e)
        sys.exit(1)
