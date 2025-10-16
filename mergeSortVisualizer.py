import tkinter as tk
from tkinter import simpledialog
import time


# Merge Sort works by dividing the array into halves recursively and 
# merging sorted halves while comparing elements.

# For visualization, the key events to show are:
#   Array being split (optional: highlight the subarray).
#   Comparing elements during merge.
#   Overwriting the array with the merged result.

# Data Representation: Represent the array as vertical bars (height = value).
# Highlights:  Currently compared elements (e.g., red) & merged result being written back (e.g., green).

class MergeSortVisualizer:
    def __init__(self, master, array):
        self.master = master 
        self.array = array.copy()
        self.originalArray = array.copy()
        self.steps = []
        self.currentStep = 0
        self.barWidth = 30
        self.canvasHeight = 300

        self.canvas = tk.Canvas(master, width=len(array)*self.barWidth + 50, height=self.canvasHeight)
        self.canvas.pack()  # Create a canvas where the array will be visualized

        # Buttons
        self.nextButton = tk.Button(master, text="Next Step", command=self.nextStep)
        self.nextButton.pack(side=tk.LEFT, padx=5)
        self.runButton = tk.Button(master, text="Run", command=self.runAll)
        self.runButton.pack(side=tk.LEFT, padx=5)
        self.resetButton = tk.Button(master, text="Reset", command=self.reset)
        self.resetButton.pack(side=tk.LEFT, padx=5)
       
        # Prepare steps
        self.prepareSteps()
        self.drawArray()

    def prepareSteps(self):
        # Merge Sort Algorithm Function and the steps to visualize it

        def mergeSort(arr, start, end, steps):
            if end - start > 1:  # if the array has over one element, sort
                mid = (start + end) // 2
                mergeSort(arr, start, mid, steps)  # recursively divide the array by the midpoint
                mergeSort(arr, mid, end, steps)
                merge(arr, start, mid, end, steps)  # merge the divided halves

        def merge(arr, start, mid, end, steps):
            left = arr[start:mid]
            right = arr[mid:end]  # make two arrays as each half of the input array
            i = j = 0  # instantiate array iterators
            k = start

            # Merge elements from left and right arrays back into the array in sorted order
            while i < len(left) and j < len(right):
                steps.append(("compare", start + i, mid + j))  # record comparison
                
                if left[i] <= right[j]:
                    steps.append(("overwrite", k, left[i]))  # record overwrite
                    arr[k] = left[i]
                    i += 1
                else:
                    steps.append(("overwrite", k, right[j]))  # record overwrite
                    arr[k] = right[j]
                    j += 1
                
                k += 1  # move to the next position in the merged array

            # Copy remaining elements
            while i < len(left):
                steps.append(("overwrite", k, left[i]))
                arr[k] = left[i]
                i += 1
                k += 1

            while j < len(right):
                steps.append(("overwrite", k, right[j]))
                arr[k] = right[j]
                j += 1
                k += 1

        arrCopy = self.array.copy()
        mergeSort(arrCopy, 0, len(arrCopy), self.steps)

    def nextStep(self):
        


    def nextStep(self):
        # Apply the next operation to the array
        pass

    def isDone(self):
        return self.currentStep >= len(self.steps)
