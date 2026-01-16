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
- Reverse is implemented via snapshots (restore + replay), not per-event undo.
"""


class SortingVisualizerBase(ABC):
    """
    Base class for all sorting visualizers.

    Provides:
      - event timeline storage
      - snapshot-based rewind support
      - play / pause / speed control
      - array mutation based on abstract events

    Subclasses provide:
      - generate_events(arr_copy): yields compare/swap/overwrite events
    """

    def __init__(self, array, checkpoint_every=50):
        # Original immutable input (used for reset)
        self.original = array.copy()

        # Live array displayed by the renderer (mutated ONLY by _apply_event)
        self.array = array.copy()

        # -------------------------------
        # Event timeline (time-travel)
        # -------------------------------

        # All events generated so far (replayable)
        self.events = []

        # Index of the *next* event to apply (playhead)
        self.event_index = 0

        # -------------------------------
        # Snapshots (for reverse)
        # -------------------------------

        # How often we store full array snapshots
        self.checkpoint_every = checkpoint_every

        # Each checkpoint: (event_index, snapshot_of_array)
        self.checkpoints = [(0, self.original.copy())]

        # -------------------------------
        # Playback state
        # -------------------------------

        self.is_playing = False
        self.speed = 5  # events per tick/frame

        # -------------------------------
        # Highlight state (for renderer)
        # -------------------------------

        self.highlight = {
            "compare": None,    # tuple (i, j)
            "swap": None,       # tuple (i, j)
            "overwrite": None   # index k
        }

        # -------------------------------
        # Algorithm generator
        # -------------------------------

        # Generator runs on its OWN working copy (never touches self.array)
        self._gen = self.generate_events(self.array.copy())

    @abstractmethod
    def generate_events(self, array_copy):
        """
        Subclasses implement this method.

        Must yield events using the shared contract.
        Must not touch UI, timing, or self.array.
        """
        raise NotImplementedError

    def reset(self):
        """
        Restore initial state:
          - reset array
          - clear timeline
          - clear checkpoints
          - restart generator
        """
        self.array = self.original.copy()
        self.events.clear()
        self.event_index = 0
        self.checkpoints = [(0, self.original.copy())]
        self.is_playing = False
        self.highlight = {"compare": None, "swap": None, "overwrite": None}
        self._gen = self.generate_events(self.array.copy())

    # -------------------------------
    # Forward event application
    # -------------------------------

    def _apply_event(self, event):
        """
        Apply one event to self.array.

        This is the ONLY place where self.array is mutated.
        """
        t = event["type"]

        # Clear highlights each event
        self.highlight = {"compare": None, "swap": None, "overwrite": None}

        if t == "compare":
            # No mutation; just highlight
            self.highlight["compare"] = (event["i"], event["j"])

        elif t == "swap":
            # Mutate array with swap
            i, j = event["i"], event["j"]
            self.array[i], self.array[j] = self.array[j], self.array[i]
            self.highlight["swap"] = (i, j)

        elif t == "overwrite":
            # Overwrite uses "value" per shared event contract
            k = event["k"]
            self.array[k] = event["value"]
            self.highlight["overwrite"] = k

    def _maybe_checkpoint(self):
        """
        Save a full snapshot of the array every checkpoint_every events.
        Helps implement reverse by restore + replay.
        """
        if self.event_index % self.checkpoint_every == 0:
            self.checkpoints.append((self.event_index, self.array.copy()))

    def step_forward(self):
        """
        Advance by ONE event:
          - replay existing event if already generated
          - otherwise pull a new one from generator
        """
        # Replay from timeline
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

    # -------------------------------
    # Reverse (snapshot-based)
    # -------------------------------

    def _restore_to_index(self, target_index):
        """
        Restore array to an earlier event index:
          1) restore nearest checkpoint <= target_index
          2) replay forward until target_index
        """
        # Find nearest checkpoint <= target_index
        cp_idx = 0
        for i in range(len(self.checkpoints) - 1, -1, -1):
            if self.checkpoints[i][0] <= target_index:
                cp_idx = i
                break

        base_event_index, snapshot = self.checkpoints[cp_idx]
        self.array = snapshot.copy()
        self.event_index = base_event_index

        # Replay forward to target_index using already-generated events
        while self.event_index < target_index:
            event = self.events[self.event_index]
            self._apply_event(event)
            self.event_index += 1

    def step_backward(self):
        """
        Rewind by ONE event (restore + replay).
        """
        if self.event_index == 0:
            return False

        target = self.event_index - 1
        self._restore_to_index(target)
        return True

    def tick(self):
        """
        Called each frame (Pygame loop).
        If playing, advance multiple events based on speed.
        """
        if not self.is_playing:
            return

        for _ in range(self.speed):
            if not self.step_forward():
                self.is_playing = False
                break
