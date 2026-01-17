# Algorithm-Visualizer
I am making an Algorithm Visualizer with the goal of understanding algorithms deeply through visualizing them.

# Scope & Structure:

We want to visualize multiple algorithm categories:

Sorting Algorithms (Merge Sort, Quick Sort, Heap Sort)

Graph Algorithms (Dijkstra, Bellman-Ford, Kruskal, Prim)

Dynamic Programming (Visualizing DP tables for problems like Knapsack, LCS, etc.)

Data Structures (Segment Trees, Fenwick Trees (BIT))

# Visualization Framework: 

In the Python Programming Language, I used Tkinter for DP/table visualizations, and Pygame for sorting & graph animations.

# Core Design Ideas:

Algorithm classes: Each algorithm should be a class with step() method for interactivity.
Animation loop: Run a loop that calls step() and updates the screen.
Highlight operations: E.g., swapping in sorting, edge selection in graphs, DP cell updates.
User interaction: Buttons for "Next Step", "Run Automatically", "Reset", etc.

# How to Run:

0) Make sure you have Python (3.9+ recommended) annd pygame installed

# MVP:

Visualizer classes for each of the sorting algorithms, that can then be seen into pygame with functionality such as pause/play and fastwordward/reverse 

# Next Step:

Continue completion of the MVP, complete with testing, then move into implementing other algorithms