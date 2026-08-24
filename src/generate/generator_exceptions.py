class GenerationError(Exception):
    """Raised when constrained generation cannot produce a valid result.

    Covers a forbidden token being picked by a `State`, an unparseable
    generated value, or the underlying model/vocab file being unusable.
    """

    pass
