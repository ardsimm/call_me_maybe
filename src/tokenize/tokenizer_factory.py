from .tokenizer import Tokenizer


class TokenizerFactory:

    __tokenzier_instance: Tokenizer

    @staticmethod
    def get_instance() -> Tokenizer:
        raise NotImplementedError(
            "Method get_instance of TokenizerFactory" + " not yet implemented"
        )
