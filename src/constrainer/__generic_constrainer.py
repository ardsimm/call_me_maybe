from typing import List

from . import Constrainer


class GenericConstrainer(Constrainer):

    def constrain_tokens(
        self,
        tokens: List[int],
    ) -> List[int]:
        allowed_tokens = self.state.get_allowed_tokens()
        if allowed_tokens is None:
            return []
        elif not len(allowed_tokens):
            return tokens
        return [
            token
            for token in tokens
            if token in allowed_tokens
        ]

    def pick_token(
        self,
        logits: List[float]
    ) -> int:
        max_token_id = logits.index(max(logits))
        self.state.update_last_token(max_token_id)
        return max_token_id
