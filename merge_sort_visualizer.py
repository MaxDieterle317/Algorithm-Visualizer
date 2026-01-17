from sorting_visualizer_base import SortingVisualizerBase


class MergeSortVisualizer(SortingVisualizerBase):
    """
    Merge Sort visualizer that yields events using the shared contract.

    Uses a working copy (arr_copy) to maintain correct algorithm state.
    Base class applies the yielded events to self.array.
    """

    def generate_events(self, arr_copy):
        # Optional: focus whole array at start
        yield {"type": "range", "kind": "focus", "start": 0, "end": len(arr_copy)}
        yield from self._merge_sort_steps(arr_copy, 0, len(arr_copy))
        yield {"type": "clear", "kind": "focus"}

        # Optional: mark all sorted at end
        yield {"type": "mark", "kind": "sorted", "indices": list(range(len(arr_copy)))}

    def _merge_sort_steps(self, arr_copy, start, end):
        if end - start <= 1:
            return

        mid = (start + end) // 2

        # Focus current recursion segment (visual-only)
        yield {"type": "range", "kind": "focus", "start": start, "end": end}

        yield from self._merge_sort_steps(arr_copy, start, mid)
        yield from self._merge_sort_steps(arr_copy, mid, end)

        yield from self._merge_steps(arr_copy, start, mid, end)

        # Clear merge highlight when done
        yield {"type": "clear", "kind": "merge"}

    def _merge_steps(self, arr_copy, start, mid, end):
        left = arr_copy[start:mid]
        right = arr_copy[mid:end]

        i = j = 0
        k = start

        # Mark the merge region (visual-only)
        yield {"type": "range", "kind": "merge", "start": start, "mid": mid, "end": end}

        while i < len(left) and j < len(right):
            # Compare two logical sources, and show destination k
            yield {
                "type": "compare",
                "a": start + i,   # logical left pointer
                "b": mid + j,     # logical right pointer
                "dst": k          # where the overwrite will happen
            }

            if left[i] <= right[j]:
                arr_copy[k] = left[i]
                yield {"type": "overwrite", "k": k, "value": left[i]}
                i += 1
            else:
                arr_copy[k] = right[j]
                yield {"type": "overwrite", "k": k, "value": right[j]}
                j += 1

            k += 1

        while i < len(left):
            # Optional: still show dst
            yield {"type": "compare", "a": start + i, "b": start + i, "dst": k}
            arr_copy[k] = left[i]
            yield {"type": "overwrite", "k": k, "value": left[i]}
            i += 1
            k += 1

        while j < len(right):
            yield {"type": "compare", "a": mid + j, "b": mid + j, "dst": k}
            arr_copy[k] = right[j]
            yield {"type": "overwrite", "k": k, "value": right[j]}
            j += 1
            k += 1
