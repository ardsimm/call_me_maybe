from typing import List


class Node:

    __next: List["Node"]
    __content: str

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
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, content: str) -> None:
        if content is None or not isinstance(content, str) or content == "":
            raise ValueError("Invalid type for content attribute")
        self.__content = content

    def add_next(self, next_node: "Node") -> None:
        self.next.append(next_node)
