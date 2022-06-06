class Node:
    def __init__(self, data=0, next: "Node" = None) -> None:
        self.data = data
        self.next = next

    def copy(self) -> "Node":
        return Node(self.data, self.next.copy())

    def is_tail(self) -> bool:
        return self.next is None
    
    def __repr__(self) -> str:
        return f"Node({repr(self.data)}, next={repr(self.next)})"
