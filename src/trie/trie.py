from typing import Dict, List, Optional, cast
from src.model.model import Model
from src.tokenize.tokenizer_factory import TokenizerFactory
from src.tokenize.tokenizer_type import TokenizerType


TrieNode = Dict[int, "TrieNode"]


class Trie:
    """A token-id trie: each node maps a token id to its child node."""

    __root: TrieNode
    __quote_token: int

    def __init__(self) -> None:
        """Cache the token id of a lone double quote.

        That token is appended to every branch returned by
        `get_determinated_branch`, so a completion finished early still
        ends on the `"` that `Generator.__strip_completion` trims at.

        Raises
        ------
        ValueError
            Forwarded from `TokenizerFactory.get_instance`.
        Exception
            Any exception raised by `Small_LLM_Model.__init__` the first
            time the singleton `Model` is built (e.g. model download or
            load failure) propagates uncaught.
        """
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
        """Return the only completion left from `node`, if there is one.

        Walks down from `node` for as long as the path is forced, so a
        word whose remainder no longer involves any choice can be emitted
        in one step instead of being decoded token by token.

        A node's children are its continuation tokens plus, if a word
        ends there, every token in `Model.string_end_sequences` -- that
        second group is how a word end is recorded, since no separate
        end marker is stored. Subtracting them leaves the continuations,
        and the four possible shapes are:

        - exactly one continuation, no word end: forced, so take it and
          keep walking.
        - more than one continuation: a real branch, return None and let
          the model choose.
        - one continuation *and* a word end (`filtered_keys_len !=
          full_keys_len`): also a real choice, between stopping here and
          going on, so return None. This is the case where one word is a
          prefix of another; deciding it here would make one of the two
          unreachable.
        - no continuation: the word ends here and goes no further, so
          stop and close the string.

        Parameters
        ----------
        node : TrieNode
            The node to walk down from, i.e. the node generation has
            currently reached.

        Returns
        -------
        list of int or None
            The remaining token ids, followed by a closing quote token,
            when the path from `node` is fully determined; None when the
            model still has a choice to make.

        Raises
        ------
        GenerationError
            Forwarded from `Model.string_end_sequences` if the vocab file
            cannot be loaded.
        """
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
