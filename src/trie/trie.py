from typing import Dict, List

from src.model.model import Model

TrieNode = Dict[int, "TrieNode"]


class Trie:
    """A token-id trie: each node maps a token id to its child node."""

    __root: TrieNode

    @property
    def root(self) -> TrieNode:
        """TrieNode : The trie's root node.

        Raises
        ------
        AttributeError
            If accessed before `init_trie` has been called.
        """
        return self.__root

    def init_trie(self, words: List[List[int]]) -> None:
        """Build the trie from `words`, each terminated by any end token.

        Parameters
        ----------
        words : list of list of int
            The token-id sequences to insert. Each one is terminated by
            every token in `Model.string_end_sequences`, so a `TrieState`
            walking this trie can end the word on any of them.

        Raises
        ------
        GenerationError
            Forwarded from `Model.string_end_sequences` if the vocab file
            cannot be loaded.
        """
        self.__root = {}
        for word in words:
            current = self.root
            for token in word:
                current.setdefault(token, {})
                current = current[token]
            for end_sequence in Model.get_instance().string_end_sequences:
                current.setdefault(end_sequence, {})
