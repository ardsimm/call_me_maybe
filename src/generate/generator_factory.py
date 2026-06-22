from generator import Generator


class GeneratorFactory:

    __generator_instance: Generator

    @staticmethod
    def get_instance() -> Generator:
        raise NotImplementedError(
            "Method get_instance of GeneratorFactory"
            + " not implemented"
        )
