from typing import List, Optional

from . import Constrainer


class ConstrainerImpl(Constrainer):

    def constrain_logits(
        self,
        logits: List[float],
    ) -> List[float]:
        allowed_tokens = self.state.get_allowed_tokens()
        if allowed_tokens is not None and not len(allowed_tokens):
            return logits
        if allowed_tokens is None:
            allowed_tokens = []
        i = 0
        constrained_logits: List[float] = []
        for logit in logits:
            if i in allowed_tokens:
                constrained_logits.append(logit)
            else:
                constrained_logits.append(-1)
            i += 1
        return constrained_logits

    def pick_token(
        self,
        logits: List[float]
    ) -> Optional[int]:
        max_logit = max(logits)
        if max_logit == -1:
            return None
        max_token_id = logits.index(max_logit)
        self.state.update_last_token(max_token_id)
        return max_token_id
