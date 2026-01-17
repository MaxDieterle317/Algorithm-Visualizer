from abc import ABC, abstractmethod

"""
EVENT CONTRACT (shared across all sorting algorithms)

Allowed event types:
- {"type": "compare", "i": int, "j": int}
- {"type": "swap", "i": int, "j": int}
- {"type": "overwrite", "k": int, "value": int}

Rules:
- Subclasses ONLY yield events (no drawing, no sleeping, no touching self.array).
- Base class applies events to self.array.
- Renderer reads self.array + self.highlight and draws.
- Reverse is implemented via checkpoints (restore + replay), not per-event undo.
"""


class SortingVisualizerBase(ABC):
    def __init__(self, array, checkpoint_every=50):
        self.original = array.copy()
        self.array = array.copy()

        # ---- timeline ----
        self.events = []
        self.event_index = 0

        # ---- stats ----
        self.stats = {"comparisons": 0, "swaps": 0, "overwrites": 0}

        # ---- checkpoints ----
        self.checkpoint_every = checkpoint_every
        # (event_index, array_snapshot, stats_snapshot)
        self.checkpoints = [(0, self.original.copy(), self.stats.copy(), set())]

        # ---- playback ----
        self.is_playing = False
        self.speed = 5

        # ---- highlights ----
        self.highlight = {
            "compare": None,
            "swap": None,
            "overwrite": None,
            "sorted": set(),
        }

        # ---- generator ----
        self._gen = self.generate_events(self.array.copy())

    @abstractmethod
    def generate_events(self, array_copy):
        raise NotImplementedError

    def reset(self):
        self.array = self.original.copy()
        self.events.clear()
        self.event_index = 0

        self.stats = {"comparisons": 0, "swaps": 0, "overwrites": 0}
        self.checkpoints = [(0, self.original.copy(), self.stats.copy())]

        self.is_playing = False
        self.highlight = {"compare": None, "swap": None, "overwrite": None, "sorted": set()}
        self._gen = self.generate_events(self.array.copy())

    def _apply_event(self, event):
        t = event["type"]
        if "sorted" not in self.highlight:
            self.highlight["sorted"] = set()


        # Clear transient highlights each event (keep persistent ones like sorted)
        self.highlight["compare"] = None
        self.highlight["swap"] = None
        self.highlight["overwrite"] = None

        if t == "compare":
            if event["i"] == event["j"]:
                self.highlight["sorted"].add(event["i"])
            else:
                self.highlight["compare"] = (event["i"], event["j"])
            self.stats["comparisons"] += 1

        elif t == "swap":
            i, j = event["i"], event["j"]
            self.array[i], self.array[j] = self.array[j], self.array[i]
            self.highlight["swap"] = (i, j)
            self.stats["swaps"] += 1

        elif t == "overwrite":
            k = event["k"]
            self.array[k] = event["value"]
            self.highlight["overwrite"] = k
            self.stats["overwrites"] += 1

        else:
            raise ValueError(f"Unknown event type: {t}")

    def _maybe_checkpoint(self):
        if self.event_index % self.checkpoint_every == 0:
            self.checkpoints.append(
                (self.event_index, self.array.copy(), self.stats.copy(), self.highlight["sorted"].copy())
            )

    def step_forward(self):
        # If we rewound and then step forward, we should discard checkpoints beyond current index
        # (events are still valid; checkpoints are the only stale thing)
        while self.checkpoints and self.checkpoints[-1][0] > self.event_index:
            self.checkpoints.pop()

        # Replay existing event
        if self.event_index < len(self.events):
            event = self.events[self.event_index]
            self._apply_event(event)
            self.event_index += 1
            self._maybe_checkpoint()
            return True

        # Generate a new event
        try:
            event = next(self._gen)
        except StopIteration:
            return False

        self.events.append(event)
        self._apply_event(event)
        self.event_index += 1
        self._maybe_checkpoint()
        return True

    def _restore_to_index(self, target_index):
        # Find nearest checkpoint <= target_index
        cp_idx = 0
        for i in range(len(self.checkpoints) - 1, -1, -1):
            if self.checkpoints[i][0] <= target_index:
                cp_idx = i
                break

        base_event_index, snapshot, stats_snapshot, sorted_snapshot = self.checkpoints[cp_idx]
        self.array = snapshot.copy()
        self.stats = stats_snapshot.copy()
        self.event_index = base_event_index

        # Clear highlights for a clean restore (optional)
        self.highlight = {
            "compare": None,
            "swap": None,
            "overwrite": None,
            "sorted": sorted_snapshot.copy(),
        }
        self.highlight.setdefault("sorted", set())

        # Replay forward to target_index
        while self.event_index < target_index:
            event = self.events[self.event_index]
            self._apply_event(event)
            self.event_index += 1

    def step_backward(self):
        if self.event_index == 0:
            return False
        self._restore_to_index(self.event_index - 1)
        return True

    def tick(self):
        if not self.is_playing:
            return

        for _ in range(self.speed):
            if not self.step_forward():
                self.is_playing = False
                break
