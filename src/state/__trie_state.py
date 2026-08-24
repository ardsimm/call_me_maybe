from typing import List, Optional

from src.generate.generator_exceptions import GenerationError
from src.state.state import State
from src.trie.trie import Trie, TrieNode


class TrieState(State):
    """`State` grammar walking a token-level trie of fixed allowed words.

    Overrides `get_allowed_tokens`/`update_last_token` entirely (does not
    use `_stages`/`_stage_allowed_tokens`/`_stage_transition_tokens`).
    Must be initialized with `init_trie_state` before use.
    """

    __trie: Trie
    __current_node: TrieNode

    def __init__(self) -> None:
        """Build an empty `Trie`; call `init_trie_state` before use."""
        super().__init__()
        self.__trie = Trie()

    def init_trie_state(self, words: List[List[int]]) -> None:
        """Populate the trie with `words` and reset to its root.

        Parameters
        ----------
        words : list of list of int
            The token-id sequences this state will accept.

        Raises
        ------
        GenerationError
            Forwarded from `Model.string_end_sequences` (via `Trie.init_trie`)
            if the vocab file cannot be loaded.
        """
        self.__trie.init_trie(words)
        self.__current_node = self.__trie.root

    def get_allowed_tokens(self) -> Optional[List[int]]:
        """Return the tokens that continue a word in the trie.

        Returns
        -------
        list of int or None
            The allowed token ids, or None if the current node has none
            (a word is complete and generation should stop).

        Raises
        ------
        AttributeError
            If called before `init_trie_state` (no current node set).
        """
        allowed_tokens = list(self.__current_node.keys())
        if not len(allowed_tokens):
            return None
        return list(self.__current_node.keys())

    def update_last_token(self, token: int) -> None:
        """Advance to the trie node reached by `token`.

        Parameters
        ----------
        token : int
            The token id that was just emitted.

        Raises
        ------
        AttributeError
            If called before `init_trie_state` (no current node set).
        GenerationError
            If `token` is not a child of the current node (a forbidden
            token was picked).
        """
        next_node = self.__current_node.get(token)
        if next_node is None:
            raise GenerationError(f"A forbidden token was picked: {token} ({
                self._tokenizer.decode([token])
            })")
        self.__current_node = next_node
