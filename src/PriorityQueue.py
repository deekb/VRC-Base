def _parent(index):
    return (index - 1) // 2


def _left_child(index):
    return 2 * index + 1


def _right_child(index):
    return 2 * index + 2


class PriorityQueue:
    def __init__(self):
        self.heap = []

    def _swap(self, i, j):
        _i = self.heap[i]
        _j = self.heap[j]

        self.heap[i], self.heap[j] = _j, _i

    def _heapify_up(self, index):
        while index > 0 and self.heap[index] < self.heap[_parent(index)]:
            self._swap(index, _parent(index))
            index = _parent(index)

    def _heapify_down(self, index):
        while True:
            left_child = _left_child(index)
            right_child = _right_child(index)
            smallest = index
            heap_length = len(self.heap)

            if left_child < heap_length and self.heap[left_child] < self.heap[smallest]:
                smallest = left_child

            if right_child < heap_length and self.heap[right_child] < self.heap[smallest]:
                smallest = right_child

            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break

    def push(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            raise IndexError("Can't pop from an empty priority queue")

        self._swap(0, len(self.heap) - 1)
        item = self.heap.pop()
        self._heapify_down(0)
        return item

    def empty(self):
        return not self.heap

