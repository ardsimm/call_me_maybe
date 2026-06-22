from . import Node


class Trie:
    __root: Node

    @property
    def root(self) -> Node:
        return self.__root

    @root.setter
    def root(self, root: Node):
        if (
            root is None
            or not isinstance(root, Node)
        ):
            raise ValueError("Invalid type for root attribute")
        self.__root = root
