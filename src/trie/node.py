from typing import List


class Node:

    __next: List["Node"]
    __token_id: int

    @property
    def next(self) -> List["Node"]:
        return self.__next

    @next.setter
    def next(self, next: List["Node"]) -> None:
        if (
            next is None
            or not isinstance(next, List)
            or any(not isinstance(node, Node) for node in next)
        ):
            raise ValueError("Invalid type for next attribute")
        self.__next = next

    @property
    def token_id(self) -> int:
        return self.__token_id

    @token_id.setter
    def content(self, token_id: int) -> None:
        if token_id is None or not isinstance(token_id, int) or token_id < 0:
            raise ValueError("Invalid type for content attribute")
        self.__token_id = token_id

    def add_next(self, next_node: "Node") -> None:
        self.next.append(next_node)
