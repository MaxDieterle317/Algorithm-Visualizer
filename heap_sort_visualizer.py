from sorting_visualizer_base import SortingVisualizerBase


class HeapSortVisualizer(SortingVisualizerBase):
    """
    Heap Sort that emits:
      - compare events during heapify
      - swap events when swapping nodes or extracting max
    """

    def generate_events(self, arr_copy):
        n = len(arr_copy)

        # Build a max heap
        for i in range(n // 2 - 1, -1, -1):
            yield from self._heapify(arr_copy, n, i)

        # Extract max one by one
        for end in range(n - 1, 0, -1):
            # Swap max (root) with the end element
            arr_copy[0], arr_copy[end] = arr_copy[end], arr_copy[0]
            yield {"type": "swap", "i": 0, "j": end}

            # Restore heap property on the reduced heap
            yield from self._heapify(arr_copy, end, 0)

    def _heapify(self, arr_copy, heap_size, root):
        """
        Sift-down heapify for max-heap.
        heap_size defines the active heap range [0, heap_size).
        """
        largest = root

        while True:
            left = 2 * largest + 1
            right = 2 * largest + 2
            new_largest = largest

            # Compare left child with current largest
            if left < heap_size:
                yield {"type": "compare", "i": left, "j": new_largest}
                if arr_copy[left] > arr_copy[new_largest]:
                    new_largest = left

            # Compare right child with current largest
            if right < heap_size:
                yield {"type": "compare", "i": right, "j": new_largest}
                if arr_copy[right] > arr_copy[new_largest]:
                    new_largest = right

            # If largest doesn't change, heap property is satisfied
            if new_largest == largest:
                break

            # Swap and continue sifting down
            arr_copy[largest], arr_copy[new_largest] = arr_copy[new_largest], arr_copy[largest]
            yield {"type": "swap", "i": largest, "j": new_largest}

            largest = new_largest
