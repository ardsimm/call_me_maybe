from parser import Parser


class ParserFactory:

    __parser_instance: Parser

    @staticmethod
    def get_instance() -> Parser:
        raise NotImplementedError(
            "Method get_instance of ParserFactory" + " not yet implemented"
        )
