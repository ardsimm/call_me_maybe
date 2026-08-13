from typing import List, Optional

from src.generate.generator_exceptions import GenerationError
from src.state.state import State
from src.trie.trie import Trie, TrieNode


class TrieState(State):

    __trie: Trie
    __current_node: TrieNode

    def __init__(self) -> None:
        super().__init__()
        self.__trie = Trie()

    def init_trie_state(self, words: List[List[int]]) -> None:
        self.__trie.init_trie(words)
        self.__current_node = self.__trie.root

    def get_allowed_tokens(self) -> Optional[List[int]]:
        allowed_tokens = list(self.__current_node.keys())
        if not len(allowed_tokens):
            return None
        return list(self.__current_node.keys())

    def update_last_token(self, token: int) -> None:
        next_node = self.__current_node.get(token)
        if next_node is None:
            raise GenerationError(f"A forbidden token was picked: {token} ({
                self._tokenizer.decode([token])
            })")
        self.__current_node = next_node
