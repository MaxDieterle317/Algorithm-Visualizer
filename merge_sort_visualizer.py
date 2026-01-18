import os
print("IMPORTING merge_sort_visualizer.py FROM:", os.path.abspath(__file__))

from sorting_visualizer_base import SortingVisualizerBase


class MergeSortVisualizer(SortingVisualizerBase):
    """
    Merge Sort visualizer that yields events using the shared contract.

    Contract event types ONLY:
      - {"type": "compare", "i": int, "j": int}
      - {"type": "overwrite", "k": int, "value": int}

    Uses a working copy (arr_copy) to maintain correct algorithm state.
    Base class applies the yielded events to self.array.
    """
    NAME = "Merge Sort"

    def generate_events(self, arr_copy):
        yield from self._merge_sort_steps(arr_copy, 0, len(arr_copy))

    def _merge_sort_steps(self, arr_copy, start, end):
        if end - start <= 1:
            return

        mid = (start + end) // 2

        yield from self._merge_sort_steps(arr_copy, start, mid)
        yield from self._merge_sort_steps(arr_copy, mid, end)
        yield from self._merge_steps(arr_copy, start, mid, end)

    def _merge_steps(self, arr_copy, start, mid, end):
        left = arr_copy[start:mid]
        right = arr_copy[mid:end]

        i = j = 0
        k = start

        while i < len(left) and j < len(right):
            # Visual-only compare between the two sources
            yield {"type": "compare", "i": start + i, "j": mid + j}

            if left[i] <= right[j]:
                arr_copy[k] = left[i]
                yield {"type": "overwrite", "k": k, "value": left[i]}
                i += 1
            else:
                arr_copy[k] = right[j]
                yield {"type": "overwrite", "k": k, "value": right[j]}
                j += 1

            k += 1

        # Drain leftovers (still overwrite events; compare can highlight source)
        while i < len(left):
            yield {"type": "compare", "i": start + i, "j": start + i}
            arr_copy[k] = left[i]
            yield {"type": "overwrite", "k": k, "value": left[i]}
            i += 1
            k += 1

        while j < len(right):
            yield {"type": "compare", "i": mid + j, "j": mid + j}
            arr_copy[k] = right[j]
            yield {"type": "overwrite", "k": k, "value": right[j]}
            j += 1
            k += 1
