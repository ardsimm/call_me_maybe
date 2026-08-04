from typing import Dict, List

from src.model.model import Model


TrieNode = Dict[int, "TrieNode"]


class Trie:
    __root: TrieNode

    @property
    def root(self) -> TrieNode:
        return self.__root

    def init_trie(self, words: List[List[int]]) -> None:
        self.__root = {}
        for word in words:
            current = self.root
            for token in word:
                current.setdefault(token, {})
                current = current[token]
            for end_sequence in Model.get_instance().string_end_sequences:
                current.setdefault(end_sequence, {})
