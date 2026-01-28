# ================================================
# 3. SET OPERATIONS (UNORDERED, UNIQUE)
# ================================================

# Sets are:
# - Unordered (no index positions)
# - Mutable (can add/remove elements)
# - Store UNIQUE elements only
# - Optimized for fast membership testing
# - Commonly used for de-duplication and set math

# ------------------------------------------------
# 3.1 Creating a Set
# ------------------------------------------------

s1 = {1, 2, 3}
s2 = set([3, 4, 5])   # Using set() constructor

print(s1)
print(s2)

# Duplicate values are automatically removed
duplicates = {1, 2, 2, 3, 3}
print(duplicates)    # {1, 2, 3}

# ------------------------------------------------
# 3.2 Empty Set (IMPORTANT)
# ------------------------------------------------

empty_set = set()    # ❗ {} creates a dictionary, not a set
print(type(empty_set))  # <class 'set'>

# ------------------------------------------------
# 3.3 Adding Elements
# ------------------------------------------------

# add() – Add ONE element
s = {1, 2}
s.add(3)
print(s)

# update() – Add MULTIPLE elements
s.update([4, 5, 6])
print(s)

# ------------------------------------------------
# 3.4 Removing Elements
# ------------------------------------------------

# remove() – Raises ERROR if element not found
s.remove(3)
print(s)

# discard() – SAFE removal (no error if missing)
s.discard(10)
print(s)

# pop() – Removes and returns a RANDOM element
removed = s.pop()
print(removed)
print(s)

# clear() – Remove ALL elements
s.clear()
print(s)  # set()

# ------------------------------------------------
# 3.5 Membership Testing (VERY FAST)
# ------------------------------------------------

nums = {10, 20, 30}

print(20 in nums)    # True
print(100 in nums)   # False

# ------------------------------------------------
# 3.6 Set Length
# ------------------------------------------------

print(len(nums))     # 3

# ------------------------------------------------
# 3.7 Iterating Over a Set
# ------------------------------------------------

for value in nums:
    print(value)

# Order is NOT guaranteed

# ------------------------------------------------
# 3.8 Set Union
# ------------------------------------------------

a = {1, 2, 3}
b = {3, 4, 5}

print(a | b)               # {1, 2, 3, 4, 5}
print(a.union(b))          # Same as above

# ------------------------------------------------
# 3.9 Set Intersection
# ------------------------------------------------

print(a & b)               # {3}
print(a.intersection(b))   # Same as above

# ------------------------------------------------
# 3.10 Set Difference
# ------------------------------------------------

print(a - b)               # {1, 2}
print(a.difference(b))     # Same as above

# ------------------------------------------------
# 3.11 Symmetric Difference
# ------------------------------------------------

print(a ^ b)                       # {1, 2, 4, 5}
print(a.symmetric_difference(b))   # Same as above

# ------------------------------------------------
# 3.12 Subset & Superset Checks
# ------------------------------------------------

small = {1, 2}
large = {1, 2, 3, 4}

print(small.issubset(large))       # True
print(large.issuperset(small))     # True

# ------------------------------------------------
# 3.13 Disjoint Sets
# ------------------------------------------------

x = {1, 2}
y = {3, 4}

print(x.isdisjoint(y))     # True

# ------------------------------------------------
# 3.14 Copying Sets (Shallow Copy)
# ------------------------------------------------

a = {1, 2, 3}
b = a.copy()

b.add(4)

print(a)   # {1, 2, 3}
print(b)   # {1, 2, 3, 4}

# ------------------------------------------------
# 3.15 Frozen Set (IMMUTABLE SET)
# ------------------------------------------------

fs = frozenset([1, 2, 3])

# fs.add(4)  ❌ ERROR: frozenset is immutable

print(fs)

# ------------------------------------------------
# 3.16 Using Sets for De-duplication (COMMON USE CASE)
# ------------------------------------------------

nums = [1, 2, 2, 3, 3, 4]

unique_nums = set(nums)
print(unique_nums)

# ------------------------------------------------
# 3.17 Converting Set to List
# ------------------------------------------------

s = {5, 1, 3}
lst = list(s)

print(lst)   # Order not guaranteed

# ------------------------------------------------
# 3.18 Using Sets in Real-World Scenarios
# ------------------------------------------------

# Example: Finding common users between two systems
users_app1 = {"alice", "bob", "charlie"}
users_app2 = {"bob", "david"}

common_users = users_app1 & users_app2
print(common_users)

# ================================================
# END OF SET OPERATIONS
# ================================================
