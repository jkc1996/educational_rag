# ================================================
# 1. NUMPY BASICS (ARRAYS & MATRICES)
# ================================================

# NumPy (Numerical Python) is the foundation of Data Science.
# - Faster than Lists (written in C)
# - Supports Vectorization (Math without loops)
# - Memory Efficient

import numpy as np

# ------------------------------------------------
# 1.1 Creating Arrays
# ------------------------------------------------

# From a Python List
arr = np.array([1, 2, 3, 4, 5])
print(arr)  # [1 2 3 4 5]

# arange() - Like Python's range()
# Generates [0, 2, 4, 6, 8]
print(np.arange(0, 10, 2))

arr = np.arange(18, 10, -2) # [18 16 14 12]

# zeros() - Array of all 0s (Float by default)
print(np.zeros(5))  # [0. 0. 0. 0. 0.]

print(np.zeros((5,2))) 

#output of above:

# [[0. 0.]
#  [0. 0.]
#  [0. 0.]
#  [0. 0.]
#  [0. 0.]]

# ones() - Array of all 1s
# Creates a 2x3 Matrix
print(np.ones((2, 3)))

# linspace() - "Linear Space"
# Generates 5 evenly spaced numbers between 0 and 1
print(np.linspace(0, 1, 5)) 
# Output: [0.   0.25 0.5  0.75 1.  ]

# ------------------------------------------------
# 1.2 Inspection (Know Your Data)
# ------------------------------------------------
matrix = np.array([[1, 2, 3], [4, 5, 6]])

# .shape - Returns tuple (rows, columns)
print(matrix.shape)  # (2, 3)

# .ndim - Number of dimensions
print(matrix.ndim)   # 2

# .dtype - Data type inside the array
# (NumPy arrays must have ONE consistent type)
print(matrix.dtype)  # int64 (or int32)

# ------------------------------------------------
# 1.3 Reshaping (Changing Dimensions)
# ------------------------------------------------
arr = np.arange(12)  # [0, 1, ... 11]

# Convert 1D array to 2D matrix (3 rows, 4 cols)
# Note: Total elements must match (3 * 4 = 12)
reshaped = arr.reshape(3, 4)

print(reshaped)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]

# ------------------------------------------------
# 1.4 Vectorization (Math without Loops)
# ------------------------------------------------
arr = np.array([1, 2, 3, 4])

# Multiply every item by 2 instantly
print(arr * 2)      # [2 4 6 8]

# Add 10 to every item
print(arr + 10)     # [11 12 13 14]

# Compare every item
print(arr > 2)      # [False False  True  True]

# ------------------------------------------------
# 1.5 Indexing & Slicing
# ------------------------------------------------

# for 1 D array slicing:

original = np.array([1, 2, 3, 4, 5])

slice_ref = original[0:2] # [1, 2]

mat = np.array([[10, 20, 30], 
                [40, 50, 60], 
                [70, 80, 90]])

# Access specific element [row, col]
print(mat[0, 1])    # 20 (Row 0, Col 1)

# Slicing [row_start:row_end, col_start:col_end]
# Get top-right 2x2 chunk
print(mat[0:2, 1:3])
# [[20 30]
#  [50 60]]

# Boolean Masking (Filtering)
# Get all numbers greater than 50
print(mat[mat > 50]) # [60 70 80 90]

# ------------------------------------------------
# 1.6 Aggregation (Statistics)
# ------------------------------------------------
arr = np.array([10, 20, 30, 40])

print(np.mean(arr)) # Average: 25.0
print(np.max(arr))  # Max: 40
print(np.min(arr))  # Min: 10
print(np.sum(arr))  # Sum: 100

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

# ================================================
# 2. NUMPY INTERMEDIATE (MANIPULATION & RANDOMNESS)
# ================================================

# ------------------------------------------------
# 2.1 The "Axis" Concept (CRITICAL)
# ------------------------------------------------
# When doing operations on 2D matrices, you must specify direction.
# axis=0 -> "Down" (Act on Columns)
# axis=1 -> "Across" (Act on Rows)

matrix = np.array([[10, 20], 
                   [30, 40]])

# Sum "Down" the columns (10+30, 20+40)
print(matrix.sum(axis=0))  # [40 60]

# Sum "Across" the rows (10+20, 30+40)
print(matrix.sum(axis=1))  # [30 70]

#min, max, mean also works with axis 0 and 1

print(matrix.mean(axis=0))

print(matrix.max(axis=0))

print(matrix.min(axis=0))

# ------------------------------------------------
# 2.2 Random Number Generation (Used heavily in ML)
# ------------------------------------------------

# 1. seed() - Makes random numbers "Reproducible"
# If you run this code 100 times, you get the exact same "random" numbers. so theese line wil have basically effect on the np.random.rand(3) and np.random.randint(1, 100, 5).
# every time we run this .py file - print(np.random.rand(3)) and print(np.random.randint(1, 100, 5))  will genrate same random numbers everytime we run.. (not like same result of 2 print stemtnt).. 
# but if we change the order of the random sttemt, then the randm number generated will be changed
# 42 is nt significant here.. it can be any fix number.. but if we change to other number then again it will give diffrent random numbers(but same for all the runs)

np.random.seed(42) 

# 2. rand() - Random floats between 0 and 1
print(np.random.rand(3))  
# Output: [0.374 0.950 0.731] (approx)

# 3. randint() - Random Integers (low, high, size)
# Generate 5 numbers between 1 and 99
print(np.random.randint(1, 100, 5)) 
# Output: [5 20 82 33 11]

# 4. shuffle() - Randomly shuffles an array IN-PLACE
nums = np.arange(5)
np.random.shuffle(nums)
print(nums) # e.g. [3 0 4 1 2]

# 5. A single random float from a normal distribution (mean = 0, standard deviation = 1)

np.random.randn() # possible output - 0.4967141530112327 (can be positive/negative)

# 6. A random element selected from a list/array

# You MUST pass options:

np.random.choice([10, 20, 30])

# Example with multiple picks:

np.random.choice([1, 2, 3, 4], size=3) # [3 1 4]

# ------------------------------------------------
# 2.3 Stacking & Concatenating (Gluing Arrays)
# ------------------------------------------------
a = np.array([1, 2])
b = np.array([3, 4])

# 1. hstack (Horizontal Stack) - Side by Side
print(np.hstack((a, b)))  
# Output: [1 2 3 4]

# 2. vstack (Vertical Stack) - Top and Bottom
print(np.vstack((a, b)))
# Output:
# [[1 2]
#  [3 4]]

# ------------------------------------------------
# 2.4 The "Copy" Trap (IMPORTANT BUG FIX)
# ------------------------------------------------
# Slicing a numpy array returns a "View" (reference), not a new copy.
# If you modify the slice, you DESTROY the original data.

original = np.array([1, 2, 3, 4, 5])

# BAD PRACTICE (Modifying slice directly)
slice_ref = original[0:2]
slice_ref[0] = 999

print(original) 
# Output: [999, 2, 3, 4, 5] <--- ORIGINAL CHANGED!

# GOOD PRACTICE (Use .copy())
original = np.array([1, 2, 3, 4, 5])
slice_copy = original[0:2].copy()
slice_copy[0] = 999

print(original)
# Output: [1, 2, 3, 4, 5] <--- Safe.

# ---------------------------------------------------------------------------------------------------------------------------------------------------------

# ================================================
# 3. NUMPY: THE LOGIC & UTILITY FUNCTIONS
# ================================================

# ------------------------------------------------
# 3.1 np.full() - The "Custom Fill" (You found this!)
# ------------------------------------------------
# Fills a matrix of specific shape with a specific number.
# Useful for initializing weights or placeholders.
mat = np.full((2, 3), 7)
print(mat)
# [[7 7 7]
#  [7 7 7]]

# ------------------------------------------------
# 3.2 np.unique() - The "Set" operation
# ------------------------------------------------
# Finds unique elements in an array (returns them sorted).
# Essential for categorical data (e.g., checking what labels exist).
arr = np.array([10, 20, 10, 30, 20, 10])

print(np.unique(arr))
# Output: [10 20 30]

# ------------------------------------------------
# 3.3 np.where() - The "Excel IF Statement" (CRITICAL)
# ------------------------------------------------
# Syntax: np.where(condition, value_if_true, value_if_false)
# This is used EVERYWHERE to clean data.

arr = np.array([10, 100, 20, 200])

# "If value > 50, replace with 'High', else 'Low'"
# (Note: NumPy converts types to handle strings here)
print(np.where(arr > 50, 'High', 'Low'))
# Output: ['Low' 'High' 'Low' 'High']

# It can also just give you the *indices* of where true exists
print(np.where(arr > 50))
# Output: (array([1, 3]),)  <- Indices 1 and 3 are > 50

# ------------------------------------------------
# 3.4 np.eye() - The "Identity Matrix"
# ------------------------------------------------
# Creates a square matrix with 1s on the diagonal and 0s elsewhere.
# Used often in Linear Algebra and Machine Learning models.
print(np.eye(3))
# [[1. 0. 0.]
#  [0. 1. 0.]
#  [0. 0. 1.]]

# ---------------------------------------------------------------------------------------------------------------------------------------------

# convertin numpy array to back to pyhon list: - This converts everything deeply. If you have a matrix, it becomes a "List of Lists".

# A 2D Matrix
arr = np.array([[1, 2], [3, 4]])

# Convert back to standard Python list
py_list = arr.tolist()

print(py_list)
# Output: [[1, 2], [3, 4]]

print(type(py_list))
# Output: <class 'list'>

# -------------------------------------------------------------------------------------------------------------------------------------------

# ================================================
# 4. NUMPY ITERATION & SPEED
# ================================================

arr = np.array([[1, 2, 3], 
                [4, 5, 6]])

# ------------------------------------------------
# 4.1 Standard Loop (Iterates Axis 0 / Rows)
# ------------------------------------------------
for x in arr:
    print(x)
# Output:
# [1 2 3]
# [4 5 6]

# ------------------------------------------------
# 4.2 Element-Wise Loop (Visiting every number)
# ------------------------------------------------
# The .flat attribute gives you a 1D iterator
for x in arr.flat:
    print(x, end=" ")
# Output: 1 2 3 4 5 6

# ------------------------------------------------
# 4.3 np.nditer() - The Efficient Iterator
# ------------------------------------------------
# Useful for large arrays where flattening is expensive
for x in np.nditer(arr):
    print(x, end=" ")
# Output: 1 2 3 4 5 6

# ------------------------------------------------
# 4.4 The "Anti-Loop" Rule (Vectorization)
# ------------------------------------------------
# BAD (Slow):
# for i in range(len(arr)):
#    arr[i] = arr[i] + 5

# GOOD (Fast):
# arr = arr + 5

# ----------------------------------------------------------------------------------------------------------------------------------------------------

# Methods to Convert a 2D NumPy Array to 1D

# Create a sample 2D array
arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(f"Original 2D array:\n{arr_2d}")

# 1. Using ravel()

# The ravel() method returns a view of the original array whenever possible (meaning no copy of the data is made),
# making it the most efficient method for large arrays. Changes to the new 1D array may affect the original array.

# that means if i do this - arr_1d_ravel[0] = 3, and then try to print "arr_2d" - the first element(0th row and 0th column) of this arry will be 3.. since this ravel() does not create copy.. but gives the view of the origanal 2d array 

arr_1d_ravel = arr_2d.ravel()
print(f"1D array using ravel(): {arr_1d_ravel}")

# 2. Using flatten()
# The flatten() method always creates a new copy of the data. Changes to the new 1D array will not affect the original array. 

arr_1d_flatten = arr_2d.flatten()
print(f"1D array using flatten(): {arr_1d_flatten}")

# 3. Using reshape(-1)
# The reshape(-1) method is a flexible way to convert an array to any dimension, including 1D.
# The -1 argument tells NumPy to automatically calculate the size of that dimension based on the total number of elements in the array. Like ravel(), it attempts to return a view first (for efficiency). 

arr_1d_reshape = arr_2d.reshape(-1)
print(f"1D array using reshape(-1): {arr_1d_reshape}")

