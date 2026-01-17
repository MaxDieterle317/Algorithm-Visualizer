import pygame


class PygameSortingApp:
    """
    Generic pygame UI for ANY SortingVisualizerBase instance.

    Controls (MVP):
      SPACE -> play/pause (forward autoplay)
      LEFT  -> hold to rewind (scrub backward)
      RIGHT -> hold to fast-forward (scrub forward)
      UP    -> increase speed
      DOWN  -> decrease speed (min 1)
      R     -> reset
      ESC   -> quit

    Behavior:
      - Holding LEFT/RIGHT pauses autoplay (video-style scrubbing).
    """

    def __init__(self, visualizer, width=1000, height=600):
        self.viz = visualizer
        self.width = width
        self.height = height
        self.acc = 0.0

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Algorithm Visualizer (Sorting MVP)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

    # --------------------------
    # Rendering
    # --------------------------

    def draw(self):
        self.screen.fill((20, 20, 20))

        arr = self.viz.array
        if not arr:
            pygame.display.flip()
            return

        n = len(arr)
        max_val = max(arr) if max(arr) != 0 else 1

        padding = 40
        usable_w = self.width - 2 * padding
        usable_h = self.height - 2 * padding
        bar_w = max(1, usable_w // n)

        hl = self.viz.highlight
        compare = hl.get("compare")
        swap = hl.get("swap")
        overwrite = hl.get("overwrite")
        sorted_set = hl.get("sorted", set())

        for i, v in enumerate(arr):
            h = int((v / max_val) * usable_h)
            x = padding + i * bar_w
            y = self.height - padding - h

            color = (120, 170, 255)  # default

            # persistent sorted baseline
            if i in sorted_set:
                color = (160, 160, 255)

            # transient overrides (your existing priority)
            if compare and i in compare:
                color = (255, 80, 80)
            if swap and i in swap:
                color = (255, 200, 80)
            if overwrite == i:
                color = (80, 255, 120)

            pygame.draw.rect(self.screen, color, (x, y, bar_w - 1, h))

        status = "PLAYING" if self.viz.is_playing else "PAUSED"
        text = (
            f"{status} | speed={self.viz.speed} | "
            f"event={self.viz.event_index}/{len(self.viz.events)} | "
            f"HOLD LEFT=rewind RIGHT=forward"
        )
        surf = self.font.render(text, True, (230, 230, 230))
        self.screen.blit(surf, (20, 10))
        
        s = self.viz.stats
        stats_line = f"cmp={s['comparisons']} swp={s['swaps']} ovr={s['overwrites']}"
        surf2 = self.font.render(stats_line, True, (230, 230, 230))
        self.screen.blit(surf2, (20, 32))

        pygame.display.flip()

    # --------------------------
    # Input handling
    # --------------------------

    def handle_keydown(self, key):
        if key == pygame.K_SPACE:
            # Toggle autoplay
            self.viz.is_playing = not self.viz.is_playing

        elif key == pygame.K_UP:
            self.viz.speed += 1

        elif key == pygame.K_DOWN:
            self.viz.speed = max(1, self.viz.speed - 1)

        elif key == pygame.K_r:
            self.viz.reset()
            self.acc = 0.0

        elif key == pygame.K_ESCAPE:
            raise SystemExit

        elif key == pygame.K_1:
            from merge_sort_visualizer import MergeSortVisualizer
            self.viz = MergeSortVisualizer(self.viz.original, checkpoint_every=self.viz.checkpoint_every)
            self.acc = 0.0

        elif key == pygame.K_2:
            from quick_sort_visualizer import QuickSortVisualizer
            self.viz = QuickSortVisualizer(self.viz.original, checkpoint_every=self.viz.checkpoint_every)
            self.acc = 0.0

        elif key == pygame.K_3:
            from heap_sort_visualizer import HeapSortVisualizer
            self.viz = HeapSortVisualizer(self.viz.original, checkpoint_every=self.viz.checkpoint_every)
            self.acc = 0.0

    # --------------------------
    # Main loop
    # --------------------------

    def run(self, fps=60):
        running = True
        self.acc = 0.0  # seconds accumulator

        while running:
            dt = self.clock.tick(fps) / 1000.0

            # Handle discrete events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    try:
                        self.handle_keydown(event.key)
                    except SystemExit:
                        running = False

            keys = pygame.key.get_pressed()

            scrubbing_left = keys[pygame.K_LEFT]
            scrubbing_right = keys[pygame.K_RIGHT]
            scrubbing = scrubbing_left or scrubbing_right

            if scrubbing:
                self.viz.is_playing = False

            # events per second -> seconds per event
            speed = max(1, self.viz.speed)
            spf = 1.0 / speed

            self.acc += dt

            # perform as many steps as accumulator allows
            while self.acc >= spf:
                self.acc -= spf

                if scrubbing_left:
                    self.viz.step_backward()
                elif scrubbing_right:
                    self.viz.step_forward()
                elif self.viz.is_playing:
                    if not self.viz.step_forward():
                        self.viz.is_playing = False
                        break
                else:
                    break

            self.draw()

        pygame.quit()
