# Algorithm-Visualizer
I am planning on making an Algorithm Visualizer with the goal of understanding algorithms deeply through visualizing them.

# Scope & Structure

We want to visualize multiple algorithm categories:

Sorting Algorithms:

Merge Sort
Quick Sort
Heap Sort

Graph Algorithms:

Dijkstra
Bellman-Ford
Kruskal
Prim

Dynamic Programming: Visualizing DP tables for problems like Knapsack, LCS, etc.

Data Structures:

Segment Trees
Fenwick Trees (BIT)

# Visualization Framework: 

In the Python Programming Language, I used Tkinter for DP/table visualizations, and Pygame for sorting & graph animations.

# Core Design Ideas:

Algorithm classes: Each algorithm should be a class with step() method for interactivity.
Animation loop: Run a loop that calls step() and updates the screen.
Highlight operations: E.g., swapping in sorting, edge selection in graphs, DP cell updates.
User interaction: Buttons for "Next Step", "Run Automatically", "Reset", etc.

# Next Step:

For example, Let's start by visualizing Merge Sort to build the base framework:
Representing the array as vertical bars, highlighting the bars being compared/merged, and
updating positions step by step. If we get this working smoothly, we can reuse the framework for Quick Sort, Heap Sort, and the others.
