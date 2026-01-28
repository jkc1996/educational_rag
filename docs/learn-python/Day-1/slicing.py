# ================================================
# SLICING IN PYTHON (list / str / tuple)
# ================================================

# Slicing syntax:
# sequence[start : stop : step]

# - start → index to begin (inclusive)
# - stop  → index to end   (exclusive)
# - step  → jump count (default = 1)

# Works on:
# - list
# - string
# - tuple

# ================================================
# 1. BASIC SLICING
# ================================================

nums = [0, 1, 2, 3, 4, 5]

print(nums[1:4])     # [1, 2, 3]
print(nums[:4])      # [0, 1, 2, 3]
print(nums[2:])      # [2, 3, 4, 5]
print(nums[:])       # FULL copy

# IMPORTANT:
# stop index is NOT included

# ================================================
# 2. NEGATIVE INDICES
# ================================================

print(nums[-3:])     # [3, 4, 5]
print(nums[:-2])     # [0, 1, 2, 3]
print(nums[-4:-1])   # [2, 3, 4]

# ================================================
# 3. STEP VALUE
# ================================================

print(nums[::2])     # [0, 2, 4]
print(nums[1::2])    # [1, 3, 5]
print(nums[::3])     # [0, 3]

# ================================================
# 4. REVERSE A SEQUENCE (VERY COMMON)
# ================================================

print(nums[::-1])    # [5, 4, 3, 2, 1, 0]

# ================================================
# 5. SLICING STRINGS
# ================================================

text = "PythonProgramming"

print(text[0:6])     # Python
print(text[6:])      # Programming
print(text[::-1])    # Reverse string

# ================================================
# 6. SLICING TUPLES
# ================================================

coords = (10, 20, 30, 40)

print(coords[1:3])   # (20, 30)

# ================================================
# 7. SLICING RETURNS A NEW OBJECT
# ================================================

nums = [1, 2, 3, 4]
copy_nums = nums[:]

copy_nums.append(5)

print(nums)       # [1, 2, 3, 4]
print(copy_nums)  # [1, 2, 3, 4, 5]

# NOTE:
# This is a SHALLOW copy

# ================================================
# 8. MODIFYING LIST USING SLICING
# ================================================

nums = [1, 2, 3, 4]

nums[1:3] = [20, 30]
print(nums)       # [1, 20, 30, 4]

# Deleting using slicing
nums[1:3] = []
print(nums)       # [1, 4]

# ================================================
# 9. STEP WITH ASSIGNMENT (ADVANCED)
# ================================================

nums = [0, 0, 0, 0, 0, 0]

nums[::2] = [1, 1, 1]
print(nums)       # [1, 0, 1, 0, 1, 0]

# Length MUST match step slice length

# ================================================
# 10. COMMON REAL-WORLD USE CASES
# ================================================

# Get last N elements
data = [10, 20, 30, 40, 50]
print(data[-3:])  # [30, 40, 50]

# Skip first element
print(data[1:])

# Copy list safely
safe_copy = data[:]

# ================================================
# SUMMARY
# ================================================

# ✔ [start:stop:step] is slicing
# ✔ stop index is exclusive
# ✔ step controls jump direction
# ✔ [:] creates a shallow copy
# ✔ [::-1] reverses a sequence
# ✔ Works on list, str, tuple
# ✔ Very common in NumPy & Pandas

# ================================================
# END OF SLICING
# ================================================
