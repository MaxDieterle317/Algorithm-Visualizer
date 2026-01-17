import os
print("IMPORTING pygame_sorting_app.py FROM:", os.path.abspath(__file__))

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
        pygame.display.set_caption("Algorithm Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

    # --------------------------
    # Rendering
    # --------------------------

    def draw(self):
        # ---- layout constants (define FIRST) ----
        HUD_HEIGHT = 90
        FOOTER_HEIGHT = 40
        SIDEBAR_WIDTH = 260
        padding = 40

        # ---- background ----
        self.screen.fill((18, 18, 18))

        # HUD bar
        pygame.draw.rect(self.screen, (28, 28, 28), (0, 0, self.width, HUD_HEIGHT))

        # Sidebar panel (right)
        pygame.draw.rect(
            self.screen,
            (22, 22, 22),
            (
                self.width - SIDEBAR_WIDTH,
                HUD_HEIGHT,
                SIDEBAR_WIDTH,
                self.height - HUD_HEIGHT - FOOTER_HEIGHT,
            ),
        )

        # Footer bar
        pygame.draw.rect(
            self.screen,
            (24, 24, 24),
            (0, self.height - FOOTER_HEIGHT, self.width, FOOTER_HEIGHT),
        )

        arr = self.viz.array
        if not arr:
            pygame.display.flip()
            return

        # ---- HUD text ----
        algo_name = getattr(self.viz, "NAME", "Unknown Algorithm")
        status = "PLAYING" if self.viz.is_playing else "PAUSED"
        s = self.viz.stats

        hud_lines = [
            f"Algorithm: {algo_name}",
            f"Status: {status}    Speed: {self.viz.speed} events/sec",
            f"Progress: {self.viz.event_index} / {len(self.viz.events)} steps    "
            f"cmp={s['comparisons']} swp={s['swaps']} ovr={s['overwrites']}",
        ]

        for idx, line in enumerate(hud_lines):
            line_surf = self.font.render(line, True, (230, 230, 230))
            self.screen.blit(line_surf, (20, 10 + idx * 24))

        # ---- controls footer ----
        controls = (
            "SPACE: Play/Pause   ←/→: Scrub   ↑/↓: Speed   R: Reset   "
            "1: Merge   2: Quick   3: Heap   ESC: Quit"
        )
        controls_surf = self.font.render(controls, True, (200, 200, 200))
        self.screen.blit(controls_surf, (20, self.height - FOOTER_HEIGHT + 10))

        # ---- legend (inside sidebar) ----
        legend_x = self.width - SIDEBAR_WIDTH + 20
        legend_y = HUD_HEIGHT + 20

        title = self.font.render("Legend", True, (230, 230, 230))
        self.screen.blit(title, (legend_x, legend_y - 24))

        legend = [
            ((255, 80, 80), "Comparison"),
            ((255, 200, 80), "Swap"),
            ((80, 255, 120), "Overwrite"),
            ((160, 160, 255), "Sorted (final)"),
        ]
        for idx, (color, label) in enumerate(legend):
            y = legend_y + idx * 26
            pygame.draw.rect(self.screen, color, (legend_x, y, 18, 18))
            label_surf = self.font.render(label, True, (220, 220, 220))
            self.screen.blit(label_surf, (legend_x + 26, y - 2))

        # ---- bar area (exclude sidebar) ----
        n = len(arr)
        max_val = max(arr) if max(arr) != 0 else 1

        top = HUD_HEIGHT + 10
        bottom = self.height - FOOTER_HEIGHT - padding
        usable_h = max(1, bottom - top)

        usable_w = self.width - SIDEBAR_WIDTH - 2 * padding
        bar_w = max(1, usable_w // n)

        hl = self.viz.highlight
        compare = hl.get("compare")
        swap = hl.get("swap")
        overwrite = hl.get("overwrite")
        sorted_set = hl.get("sorted", set())

        for i, v in enumerate(arr):
            h = int((v / max_val) * usable_h)
            x = padding + i * bar_w
            y = bottom - h

            color = (120, 170, 255)  # default
            if i in sorted_set:
                color = (160, 160, 255)

            if compare and i in compare:
                color = (255, 80, 80)
            if swap and i in swap:
                color = (255, 200, 80)
            if overwrite == i:
                color = (80, 255, 120)

            pygame.draw.rect(self.screen, color, (x, y, bar_w - 2, h))

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
