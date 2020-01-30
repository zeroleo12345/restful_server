from functools import total_ordering


@total_ordering
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None
        self.prev = None

    def __repr__(self):
        return 'Node<{}:{}>'.format(self.key, self.value)

    def __eq__(self, node):
        return self.key == node.key

    def __gt__(self, node):
        return self.key > node.key


class LinkedHashMap:
    def __init__(self):
        self._map = dict()
        self._head = None
        self._tail = None

    def get(self, key):
        return self._map.get(key, None)

    def add(self, key, value):
        node = Node(key, value)
        self._map[key] = node
        if self._head is None:
            self._head = node
            self._tail = node
        else:
            self._tail.next = node
            node.prev = self._tail
            self._tail = node
        return node

    def delete(self, key):
        node = self._map.pop(key, None)
        if node:
            if node.prev is None and node.next is None:
                self._head = None
                self._tail = None
            elif node.prev is None:
                self._head = node.next
                node.next.prev = node.prev
            elif node.next is None:
                self._tail = node.prev
                node.prev.next = node.next
            else:
                node.prev.next = node.next
                node.next.prev = node.prev
        node.next = None
        node.prev = None
        return node

    def _traverse_linked_list(self):
        p_node = self._head
        while p_node:
            yield p_node
            p_node = p_node.next

    def keys(self):
        for node in self._traverse_linked_list():
            yield node.key

    def values(self):
        for node in self._traverse_linked_list():
            yield node.value

    def items(self):
        for node in self._traverse_linked_list():
            yield node.key, node.value

    def __repr__(self):
        return 'LinkedHashMap([{}])'.format(', '.join(str(item) for item in self.items()))


if __name__ == '__main__':
    m = LinkedHashMap()
    print(f"add(a): {m.add('a', 1)}")
    print(f"add(b): {m.add('b', 2)}")
    print(f"add(c): {m.add('c', 3)}")
    print(f'm: {m}')
    print(f"get(a): {m.get('a')}")
    print(f"get(b): {m.get('b')}")
    print(f"get(b).next: {m.get('b').next}")
    print(f"get(c): {m.get('c')}")
    #
    print(f"delete(a): {m.delete('a')}")
    print(f'm: {m}')
    print(f"add(d): {m.add('d', 4)}")
    print(f"delete(c): {m.delete('c')}")
    print(f'm: {m}')
    print(f"m.items: {list(m.items())}")
    print(f"m.keys: {list(m.keys())}")
    print(f"m.values: {list(m.values())}")
