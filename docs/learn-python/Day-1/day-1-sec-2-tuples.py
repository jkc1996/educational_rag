# ================================================
# 2. TUPLE OPERATIONS (ORDERED, IMMUTABLE), indices start from '0'
# ================================================

# Tuples are:
# - Ordered
# - Immutable (cannot be changed after creation)
# - Allow duplicates
# - Faster than lists
# - Used for fixed / read-only data

# ------------------------------------------------
# 2.1 Creating a Tuple
# ------------------------------------------------

t1 = (1, 2, 3)
t2 = 1, 2, 3          # Tuple packing (parentheses optional)

print(t1)
print(t2)

# Single-element tuple (IMPORTANT)
single = (5,)         # Comma is mandatory
print(type(single))   # <class 'tuple'>

# ------------------------------------------------
# 2.2 Accessing Elements
# ------------------------------------------------

coords = (10, 20, 30)

print(coords[0])      # 10
print(coords[-1])     # 30

# ------------------------------------------------
# 2.3 Immutability (NO MODIFICATION ALLOWED)
# ------------------------------------------------

# coords[0] = 100     # ❌ ERROR: tuples are immutable

# ------------------------------------------------
# 2.4 Tuple Length
# ------------------------------------------------

print(len(coords))    # 3

# ------------------------------------------------
# 2.5 Iterating Over a Tuple
# ------------------------------------------------

for value in coords:
    print(value)

# ------------------------------------------------
# 2.6 Tuple Packing & Unpacking
# ------------------------------------------------

point = (5, 10)

x, y = point          # Unpacking
print(x)
print(y)

# Unpacking with multiple variables
a, b, c = (1, 2, 3)
print(a, b, c)

# ------------------------------------------------
# 2.7 Extended Unpacking (IMPORTANT)
# ------------------------------------------------

numbers = (1, 2, 3, 4, 5)

first, *middle, last = numbers

print(first)          # 1
print(middle)         # [2, 3, 4]
print(last)           # 5

# ------------------------------------------------
# 2.8 Tuple Concatenation (CREATES NEW TUPLE)
# ------------------------------------------------

t1 = (1, 2)
t2 = (3, 4)

t3 = t1 + t2
print(t3)             # (1, 2, 3, 4)

# ------------------------------------------------
# 2.9 Tuple Repetition
# ------------------------------------------------

t = (1, 2)
print(t * 3)          # (1, 2, 1, 2, 1, 2)

# ------------------------------------------------
# 2.10 Membership Testing
# ------------------------------------------------

nums = (10, 20, 30)

print(20 in nums)     # True
print(100 in nums)    # False

# ------------------------------------------------
# 2.11 count() – Count occurrences of a value
# ------------------------------------------------

t = (1, 2, 2, 3, 2)

print(t.count(2))     # 3

# ------------------------------------------------
# 2.12 index() – Find index of first occurrence
# ------------------------------------------------

t = (10, 20, 30)

print(t.index(20))    # 1

# ------------------------------------------------
# 2.13 Nested Tuples
# ------------------------------------------------

nested = ((1, 2), (3, 4), (5, 6))

print(nested[0])      # (1, 2)
print(nested[0][1])   # 2

# ------------------------------------------------
# 2.14 Tuple with Mutable Elements (IMPORTANT CONCEPT)
# ------------------------------------------------

t = (1, [2, 3], 4)

# The tuple itself is immutable,
# but the list INSIDE the tuple is mutable

t[1].append(5)
print(t)              # (1, [2, 3, 5], 4)

# ------------------------------------------------
# 2.15 Converting Tuple to List (COMMON PRACTICE)
# ------------------------------------------------

t = (1, 2, 3)
lst = list(t)

lst.append(4)
print(lst)            # [1, 2, 3, 4]

# ------------------------------------------------
# 2.16 Converting List to Tuple
# ------------------------------------------------

lst = [10, 20, 30]
t = tuple(lst)

print(t)              # (10, 20, 30)

# ------------------------------------------------
# 2.17 Using Tuples as Dictionary Keys
# ------------------------------------------------

# Tuples are immutable, so they can be used as dictionary keys

locations = {
    (10, 20): "Point A",
    (30, 40): "Point B"
}

print(locations[(10, 20)])

# ------------------------------------------------
# 2.18 Useful Built-in Functions with Tuples
# ------------------------------------------------

nums = (5, 1, 9, 3)

print(min(nums))      # 1
print(max(nums))      # 9
print(sum(nums))      # 18
print(sorted(nums))   # Returns LIST, not tuple

# ------------------------------------------------
# 2.19 Why Tuples are Used (Conceptual)
# ------------------------------------------------

# Tuples are preferred when:
# - Data should not change
# - Data represents a fixed structure
# - Used as dictionary keys
# - Returned from functions

# Example:
def get_user():
    return ("Jay", 29, "India")

user = get_user()
print(user)

# ================================================
# END OF TUPLE OPERATIONS
# ================================================
