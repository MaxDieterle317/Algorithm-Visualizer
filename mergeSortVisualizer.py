import tkinter as tk


class MergeSortVisualizer:
    """
    Generator-based Merge Sort visualizer.

    Architecture:
    - The merge sort generator yields "events" like:
        {"type": "compare", "i": i, "j": j}
        {"type": "overwrite", "k": k, "value": v}
    - The controller (next_step) applies those events to self.array
      and updates highlight state.
    - draw_array renders the current array + highlights.
    """

    def __init__(self, master, array):
        self.master = master

        # Data state
        self.array = array.copy()
        self.original_array = array.copy()

        # Visualization settings
        self.bar_width = 30
        self.canvas_height = 300
        self.padding = 20

        # Highlight state (used by draw_array)
        self.highlight_compare = None    # tuple (i, j)
        self.highlight_overwrite = None  # index k

        # Canvas
        canvas_width = len(self.array) * self.bar_width + 2 * self.padding
        self.canvas = tk.Canvas(master, width=canvas_width, height=self.canvas_height)
        self.canvas.pack()

        # Buttons
        self.next_button = tk.Button(master, text="Next Step", command=self.next_step)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.run_button = tk.Button(master, text="Run", command=self.run_all)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(master, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Speed (ms per event). You can later add a slider for this.
        self.delay_ms = 60

        # Run control
        self.is_running = False

        # Create the generator (stepper)
        self.stepper = self.merge_sort_steps(0, len(self.array))

        # Initial draw
        self.draw_array()

    # ---------------------------
    # Controller: step/run/reset
    # ---------------------------

    def next_step(self):
        """Consume one event from the generator and apply it to the visual state."""
        if self.stepper is None:
            return

        try:
            event = next(self.stepper)
        except StopIteration:
            # No more events: algorithm finished
            self.stepper = None
            self.is_running = False
            return

        # Clear highlights so colors don't persist incorrectly
        self.highlight_compare = None
        self.highlight_overwrite = None

        # Apply event
        if event["type"] == "compare":
            # Compare event only affects highlights
            self.highlight_compare = (event["i"], event["j"])

        elif event["type"] == "overwrite":
            # Overwrite event mutates the array at index k
            k = event["k"]
            self.array[k] = event["value"]
            self.highlight_overwrite = k

        # Redraw after applying the event
        self.draw_array()

    def run_all(self):
        """
        Automatically run events using Tkinter's after() (non-blocking).
        This keeps the UI responsive.
        """
        if self.stepper is None:
            return

        self.is_running = True

        def tick():
            # Stop if paused or finished
            if not self.is_running or self.stepper is None:
                return

            self.next_step()
            self.master.after(self.delay_ms, tick)

        tick()

    def reset(self):
        """Restore the original array and restart the generator."""
        self.is_running = False
        self.array = self.original_array.copy()
        self.highlight_compare = None
        self.highlight_overwrite = None
        self.stepper = self.merge_sort_steps(0, len(self.array))
        self.draw_array()

    # ---------------------------
    # Rendering
    # ---------------------------

    def draw_array(self):
        """Draw the array as vertical bars, with compare/overwrite highlights."""
        self.canvas.delete("all")

        if not self.array:
            return

        max_val = max(self.array) if self.array else 1

        for i, val in enumerate(self.array):
            # x coordinates for the bar
            x0 = self.padding + i * self.bar_width
            x1 = x0 + self.bar_width - 5  # small gap between bars

            # scale height to canvas space
            usable_height = self.canvas_height - 2 * self.padding
            h = int((val / max_val) * usable_height)

            # y coordinates (top to bottom)
            y1 = self.canvas_height - self.padding
            y0 = y1 - h

            # default bar color
            color = "skyblue"

            # highlight compares in red
            if self.highlight_compare and i in self.highlight_compare:
                color = "red"

            # highlight overwrites in green
            if self.highlight_overwrite == i:
                color = "green"

            # draw bar + value label
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            self.canvas.create_text((x0 + x1) / 2, y0 - 10, text=str(val), font=("Arial", 9))

    # ---------------------------
    # Generators: merge sort
    # ---------------------------

    def merge_sort_steps(self, start, end):
        """
        Recursively yield events that represent merge sort actions over self.array[start:end].
        Base case: size 0 or 1.
        """
        if end - start <= 1:
            return

        mid = (start + end) // 2

        # Sort left half (yield all its events)
        yield from self.merge_sort_steps(start, mid)

        # Sort right half (yield all its events)
        yield from self.merge_sort_steps(mid, end)

        # Merge sorted halves (yield merge events)
        yield from self.merge_steps(start, mid, end)

    def merge_steps(self, start, mid, end):
        """
        Yield compare/overwrite events for merging self.array[start:mid] and self.array[mid:end].
        Note: We copy left/right snapshots; actual writes happen via overwrite events applied by controller.
        """
        left = self.array[start:mid]
        right = self.array[mid:end]

        i = 0
        j = 0
        k = start

        # Merge while both sides have items
        while i < len(left) and j < len(right):
            # Compare the current items (global indices for visualization)
            yield {"type": "compare", "i": start + i, "j": mid + j}

            if left[i] <= right[j]:
                # Overwrite position k with left[i]
                yield {"type": "overwrite", "k": k, "value": left[i]}
                i += 1
            else:
                # Overwrite position k with right[j]
                yield {"type": "overwrite", "k": k, "value": right[j]}
                j += 1

            k += 1

        # Copy remaining left items
        while i < len(left):
            yield {"type": "overwrite", "k": k, "value": left[i]}
            i += 1
            k += 1

        # Copy remaining right items
        while j < len(right):
            yield {"type": "overwrite", "k": k, "value": right[j]}
            j += 1
            k += 1


# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Merge Sort Visualizer (Generator-based)")

    sample = [8, 3, 5, 1, 9, 2, 7, 4, 6]
    app = MergeSortVisualizer(root, sample)

    root.mainloop()
