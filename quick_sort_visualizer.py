from sorting_visualizer_base import SortingVisualizerBase


class QuickSortVisualizer(SortingVisualizerBase):
    """
    Quick Sort that emits:
      - compare events during partition
      - swap events when elements are swapped

    Uses Lomuto partition (pivot = last element) for simplicity.
    """
    NAME = "Quick Sort"

    def generate_events(self, arr_copy):
        yield from self._quick_sort(arr_copy, 0, len(arr_copy) - 1)

    def _quick_sort(self, arr_copy, low, high):
        if low >= high:
            return

        pivot_index = yield from self._partition(arr_copy, low, high)
        yield from self._quick_sort(arr_copy, low, pivot_index - 1)
        yield from self._quick_sort(arr_copy, pivot_index + 1, high)

    def _partition(self, arr_copy, low, high):
        pivot = arr_copy[high]
        i = low  # place for next "small" element

        for j in range(low, high):
            # Show boundary i and current j
            yield {"type": "compare", "i": i, "j": j}

            # Compare current element with pivot at high
            yield {"type": "compare", "i": j, "j": high}

            if arr_copy[j] <= pivot:
                if i != j:
                    arr_copy[i], arr_copy[j] = arr_copy[j], arr_copy[i]
                    yield {"type": "swap", "i": i, "j": j}
                i += 1

        # Place pivot in its final position
        if i != high:
            arr_copy[i], arr_copy[high] = arr_copy[high], arr_copy[i]
            yield {"type": "swap", "i": i, "j": high}

        return i
