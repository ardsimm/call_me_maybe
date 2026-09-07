class GenerationError(Exception):
    """Raised when generation fails for one particular prompt.

    Covers a forbidden token being picked by a `State`, an unparseable
    generated value, or a generated name matching no known function --
    all of them recoverable, in that the next prompt may well succeed.
    `CallMeMaybe.__process_prompts` catches this per prompt, logs it,
    skips that prompt, and carries on with the batch.
    """

    pass


class FatalGenerationError(Exception):
    """Raised when generation is impossible for every prompt.

    Covers the vocab file backing `Model.string_end_sequences` being
    unopenable or unparseable, and the prompt template files under
    `templates/` being missing or unreadable -- neither of which any
    later prompt could recover from. Unlike `GenerationError` this is not
    caught per prompt: it propagates out of `__process_prompts` up to
    `CallMeMaybe.run`, which logs it and abandons the run.
    """

    pass
