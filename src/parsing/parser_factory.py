from .parser import Parser
from .__argument_parser import ArgumentParser


class ParserFactory:

    __parser_instance: Parser = ArgumentParser()

    @staticmethod
    def get_instance() -> Parser:
        return ParserFactory.__parser_instance
