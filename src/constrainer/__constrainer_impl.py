from typing import List, Optional

from src.tokenize.tokenizer_factory import TokenizerFactory
from src.tokenize.tokenizer_type import TokenizerType
from . import Constrainer


class ConstrainerImpl(Constrainer):
    """Default `Constrainer`: argmax over logits restricted to `state`."""

    def pick_token(
        self,
        logits: List[float],
    ) -> Optional[int]:
        """Pick the highest-scoring token allowed by `state`, advancing it.

        If `state.get_allowed_tokens()` returns an empty list (no
        restriction), the argmax is taken over the full `logits`.

        Parameters
        ----------
        logits : list of float
            Raw per-token logits for the next generation step.

        Returns
        -------
        int or None
            The picked token id, or None if `state` signals generation is
            complete.

        Raises
        ------
        ValueError
            From `max(logits)` if `state` is unconstrained and `logits` is
            empty.
        GenerationError
            Forwarded from `state.update_last_token` if it rejects the
            picked token (only possible for a `State` whose allowed tokens
            do not match what it accepts internally).
        """
        allowed_tokens = self.state.get_allowed_tokens()
        if allowed_tokens is None:
            print(
                "No more allowed tokens, model generated:",
                TokenizerFactory.get_instance(TokenizerType.DEFAULT).decode(
                    [logits.index(max(logits))]
                ),
            )
            return None
        if not len(allowed_tokens):
            token = logits.index(max(logits))
        else:
            token = max(allowed_tokens, key=logits.__getitem__)
        self.state.update_last_token(token)
        return token
