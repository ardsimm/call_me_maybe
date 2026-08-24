from typing import List, Optional

from src.tokenize.tokenizer_factory import TokenizerFactory
from src.tokenize.tokenizer_type import TokenizerType
from . import Constrainer


class ConstrainerImpl(Constrainer):

    def pick_token(
        self,
        logits: List[float],
    ) -> Optional[int]:
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
