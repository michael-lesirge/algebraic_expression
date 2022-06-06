from linked_list import Node



class LinkedList:
    def __init__(self, iterable=None) -> None:
        self.head = None
        self.tail = None
        self.len = 0
        if iterable:
            self.extend(iterable)
    
    def append(self, object, /) -> None:
        """
        Append object to end of linked list.
        """
        new = Node(object)
        if self.is_empty():
            self.head = new
        else:
            self.tail.next = new
        self.tail = new
        self.len += 1

    def prepend(self, object, /) -> None:
        """
        Prepend object to front of linked list.
        """
        self.head = Node(object, self.head)

        self.len += 1
        
    def extend(self, iterable, /) -> None:
        """
        exstend linked list by appending elem from iterable.
        """
        for elem in iterable:
            self.append(elem)

    def clear(self) -> None:
        self.head = None
        self.len = 0

    def copy(self) -> "LinkedList":
        """
        Return a copy of the list.
        """
        copy = LinkedList()
        copy.head = self.head.copy()
        copy.len = self.len
        return copy
    
    def count(self, value, /) -> int:
        """
        Return number of occurrences of value.
        """
        count = 0
        for item in self:
            count += (value == item)
        return count
    
    def display(self) -> str:
        nodes = []
        current = self.head

        while current is not None:
            if current is self.head:
                nodes.append("[Head: %s]" % repr(current.data))
            elif current is self.tail:
                nodes.append("[Tail: %s]" % repr(current.data))
            else:
                nodes.append("[%s]" % repr(current.data))

            current = current.next

        return " -> ".join(nodes)

    def index(self, value, /) -> int:
        """
        Return first index of value.

        Raises ValueError if the value is not present.
        """
        for index, item in enumerate(self):
            if (value == item):
                return index
        raise ValueError(f"{value} is not in linked list")
    
    def insert(self, index, object, /) -> None:
        """
        Insert object before index.
        """

    def pop(self, index, /):
        """
        Remove and return item at index (default last).

        Raises IndexError if list is empty or index is out of range.
        """
        if index >= len(self):
            raise IndexError("pop " + ("index out of range" if self else "from empty list"))

        self.len -= 1

    def remove(self, value, /) -> None:
        current = self.head

        self.len -= 1

    def reverse(self) -> None:
        pass

    def sort(self, *, key=None, reverse: bool =False) -> None:
        pass
    
    def __bool__(self) -> bool:
        return self.head != None

    def __contains__(self, value) -> bool:
        for item in self:
            if item == value:
                return True
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LinkedList):
            return False
        if len(self) != len(other):
            return False
        for item, other_item in zip(self, other):
            if item != other_item:
                return False
        return True

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, LinkedList):
            return True
        if len(self) != len(other):
            return True
        for item, other_item in zip(self, other):
            if item != other_item:
                return True
        return False

    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __repr__(self) -> str:
        return repr(self.head)
    
    def __str__(self) -> str:
        return "[" + ", ".join(map(repr, self)) + "]"