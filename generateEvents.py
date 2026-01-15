from abc import ABC, abstractmethod 


class SortingVisualizerBase(ABC):
    """
    Base class for all sorting visualizers.
    Subclasses are responsible for:
      - generating algorithm-specific events
    """

    def __init__(self, array, checkpoint_every=50):
        self.original = array.copy() #original input for reset

        self.array = array.copy()  #live array displayed by the visualizer

        # -----------------------------------
        # Event timeline (time-travel support)
        # -----------------------------------'

        self.events = [] #all events that have been generated so far

        self.event_index = 0 #index of the next event

        # -----------------------------------
        # Snapshot system (for reverse)
        # -----------------------------------

        self.checkpoint_every = checkpoint_every #how often to store full array snapshots

        #each checkpoint is (event_index, array_snapshot)
        self.checkpoints = [(0, self.original.copy())]

        # -----------------------------------
        # Playback state
        # -----------------------------------

        #is auto-play active?
        self.is_playing = False

        #events to apply per tick/frame
        self.speed = 5

        # -----------------------------------
        # Highlight state (used by renderer)
        # -----------------------------------

        #renderer reads this to decide which bars to color
        self.highlight = {
            "compare": None,    # (i, j)
            "swap": None,       # (i, j)
            "overwrite": None   # k
        }

        # -----------------------------------
        # Algorithm event generator
        # -----------------------------------

        #produces abstract algorithm events using its own array copy
        self._gen = self.generate_events(self.array.copy())

        @abstractmethod
        def generateEvents(self, array_copy):
            """
            Subclasses implement this method, which:
              - describes WHAT happens
              - does NOT apply changes
              - does NOT interact with UI or timing
            """
            raise NotImplementedError

        def reset(self):
            """
            - Resets array
            - Clears event timeline
            - Clears checkpoints
            - Restarts algorithm generator
            """
            self.array = self.original.copy()
            self.events.clear()
            self.event_index = 0
            self.checkpoints = [(0, self.original.copy())]
            self.is_playing = False
            self.highlight = {"compare": None, "swap": None, "overwrite": None}
            self._gen = self.generate_events(self.array.copy())

    # -----------------------------------
    # Event application (forward playback)
    # -----------------------------------

        def _apply_event(self, event):
            """
            Applies a single algorithm event to the array, altering the array
            """
            t = event["type"]

            #clear previous highlights
            self.highlight = {"compare": None, "swap": None, "overwrite": None}

            if t == "compare":
                #compare does not change array contents
                self.highlight["compare"] = (event["i"], event["j"])

            elif t == "swap":
                #swap elements
                i, j = event["i"], event["j"]
                self.array[i], self.array[j] = self.array[j], self.array[i]
                self.highlight["swap"] = (i, j)

            elif t == "overwrite":
                #overwrite index 
                k = event["k"]
                self.array[k] = event["new"]
                self.highlight["overwrite"] = k

        def _maybe_checkpoint(self):
            """
            Saves a full snapshot of the array at regular intervals.
            Used to enable efficient rewind.
            """
            if self.event_index % self.checkpoint_every == 0:
                self.checkpoints.append((self.event_index, self.array.copy()))

        def step_forward(self):
            """
            Advances the visualization by ONE event.
            - Replays existing events if possible
            - Otherwise pulls a new event from the generator
            """
            if self.event_index < len(self.events):
                event = self.events[self.event_index]
                self._apply_event(event)
                self.event_index += 1
                self._maybe_checkpoint()
                return True

            try:
                event = next(self._gen)
            except StopIteration:
                return False

            self.events.append(event)
            self._apply_event(event)
            self.event_index += 1
            self._maybe_checkpoint()
            return True

    # -----------------------------------
    # Reverse playback (snapshot-based)
    # -----------------------------------

        def _restore_to_index(self, target_index):
            """
            Restores array state to a specific event index.

            Steps:
              1) Load nearest checkpoint <= target_index
              2) Replay events forward until target_index
            """
            cp_idx = 0
            for i in range(len(self.checkpoints) - 1, -1, -1):
                if self.checkpoints[i][0] <= target_index:
                    cp_idx = i
                    break

            base_event_index, snapshot = self.checkpoints[cp_idx]
            self.array = snapshot.copy()
            self.event_index = base_event_index

            while self.event_index < target_index:
                event = self.events[self.event_index]
                self._apply_event(event)
                self.event_index += 1

        def step_backward(self):
            """
            Rewind the visualization by ONE event.

            Implemented by restoring from a checkpoint and replaying.
            """
            if self.event_index == 0:
                return False

            target = self.event_index - 1
            self._restore_to_index(target)
            return True

        def tick(self):
            """
            Called once per frame (e.g. in Pygame).

            Advances multiple events if auto-play is enabled.
            """
            if not self.is_playing:
                return

            for _ in range(self.speed):
                if not self.step_forward():
                    self.is_playing = False
                    break

