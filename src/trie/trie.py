from typing import Dict, List, Optional, cast
from src.model.model import Model
from src.tokenize.tokenizer_factory import TokenizerFactory
from src.tokenize.tokenizer_type import TokenizerType


TrieNode = Dict[int, "TrieNode"]


END_OF_BRANCH = -1


class Trie:
    """A token-id trie: each node maps a token id to its child node."""

    __root: TrieNode
    __quote_token: int

    def __init__(self) -> None:
        self.__quote_token = cast(
            int,
            TokenizerFactory.get_instance(
                TokenizerType.DEFAULT
            ).encode("\"").tolist()[0][0]
        )

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

    def get_determinated_branch(
        self,
        node: TrieNode
    ) -> Optional[List[int]]:
        tokens: List[int] = []
        curr_node: Optional[TrieNode] = node
        while curr_node is not None:
            filtered_keys = (
                set(curr_node.keys())
                - Model.get_instance().string_end_sequences
            )
            filtered_keys_len = len(filtered_keys)
            full_keys_len = len(curr_node.keys())
            if (
                filtered_keys_len > 1
                or (
                    filtered_keys_len == 1
                    and filtered_keys_len != full_keys_len
                )
            ):
                return None
            if filtered_keys_len == 0:
                curr_node = None
            else:
                next_key = next(iter(filtered_keys))
                tokens.append(next_key)
                curr_node = curr_node.get(next_key)
        tokens.append(self.__quote_token)
        return tokens
