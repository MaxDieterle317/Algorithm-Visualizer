from merge_sort_visualizer import MergeSortVisualizer
from quick_sort_visualizer import QuickSortVisualizer
from heap_sort_visualizer import HeapSortVisualizer
from pygame_sorting_app import PygameSortingApp

if __name__ == "__main__":
    arr = [8, 3, 5, 1, 9, 2, 7, 4, 6]

    algo = "quick"  # "merge" | "quick" | "heap"

    if algo == "merge":
        viz = MergeSortVisualizer(arr, checkpoint_every=50)
    elif algo == "quick":
        viz = QuickSortVisualizer(arr, checkpoint_every=50)
    else:
        viz = HeapSortVisualizer(arr, checkpoint_every=50)

    app = PygameSortingApp(viz, width=1000, height=600)
    app.run()
