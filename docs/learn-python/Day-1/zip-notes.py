# ================================================
# ZIP() FUNCTION IN PYTHON
# ================================================

# zip() is used to COMBINE multiple iterables
# (like list, tuple, string) element-by-element.

# It pairs items based on POSITION (index)
# and returns tuples of paired values.

# Think of zip() like a zipper — joining two sides together.

# ================================================
# 1. BASIC ZIP() WITH LISTS
# ================================================

a = [1, 2, 3]
b = [4, 5, 6]

zipped = list(zip(a, b))
print(zipped)

# Output:
# [(1, 4), (2, 5), (3, 6)]

# Meaning:
# 1 pairs with 4
# 2 pairs with 5
# 3 pairs with 6


# ================================================
# 2. LOOPING USING ZIP()
# ================================================

names = ["Jay", "Amit", "Sara"]
scores = [90, 85, 92]

for name, score in zip(names, scores):
    print(name, score)

# Output:
# Jay 90
# Amit 85
# Sara 92


# ================================================
# 3. ZIP() FOR MATH OPERATIONS
# ================================================

nums1 = [1, 3, 5]
nums2 = [2, 4, 6]

result = []

for a, b in zip(nums1, nums2):
    result.append(a - b)

print(result)

# Output:
# [-1, -1, -1]


# ================================================
# 4. ZIP() WITH LIST SLICING (PAIRING ODD & EVEN)
# ================================================

nums = [1, 2, 3, 4, 5, 6]

odd = nums[::2]   # [1, 3, 5]
even = nums[1::2] # [2, 4, 6]

final_result = []

for a, b in zip(odd, even):
    final_result.append(a - b)

print(final_result)

# Output:
# [-1, -1, -1]


# ================================================
# 5. ZIP() WITH STRINGS
# ================================================

for a, b in zip("abc", "xyz"):
    print(a, b)

# Output:
# a x
# b y
# c z


# ================================================
# 6. ZIP() WITH TUPLES
# ================================================

print(list(zip((1, 2), (3, 4))))

# Output:
# [(1, 3), (2, 4)]


# ================================================
# 7. ZIP() STOPS AT SHORTEST ITERABLE
# ================================================

print(list(zip([1, 2, 3], [10, 20])))

# Output:
# [(1, 10), (2, 20)]

# zip() stops when the shorter iterable ends


# ================================================
# 8. ZIP() WITH DICTIONARIES
# ================================================

d1 = {"a": 1, "b": 2}
d2 = {"x": 10, "y": 20}

for k1, k2 in zip(d1, d2):
    print(k1, k2)

# Output:
# a x
# b y


# ================================================
# 9. KEY TAKEAWAYS — ZIP()
# ================================================

# - zip() pairs values position-wise
# - Works with list, tuple, string, dict, range, generator
# - Stops at shortest iterable
# - Cleaner and safer than nested loops
# - Great for pairing related data
