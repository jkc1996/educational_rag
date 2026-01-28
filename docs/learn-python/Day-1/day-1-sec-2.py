a = 10
b = a

# Memory idea:
# - Object 10 exists once
# - a and b both refer to the same object

print("value of a and b: ",a,b)

# Reassignment:
a = 20

# Result:
# - New object 20 is created
# - a now refers to 20
# - b still refers to 10
print("value of a and b: ",a,b)

# 2. PRIMITIVE DATA TYPES
# ================================================

# ------------------------------------------------
# 2.1 int (Integer)
# ------------------------------------------------
# Whole numbers (positive, negative, zero)

x = 10
y = -5

print(type(x))  # <class 'int'>

# ------------------------------------------------
# 2.2 float (Floating Point)
# ------------------------------------------------
# Decimal numbers

pi = 3.14
temp = -2.5

print(type(pi))  # <class 'float'>

# ------------------------------------------------
# 2.3 complex
# ------------------------------------------------
# Numbers with real and imaginary parts

z = 3 + 4j

print(type(z))  # <class 'complex'>

# ------------------------------------------------
# 2.4 bool (Boolean)
# ------------------------------------------------
# Represents truth values

is_active = True
is_admin = False

print(type(is_active))  # <class 'bool'>

# ------------------------------------------------
# 2.5 str (String)
# ------------------------------------------------
# Sequence of characters (IMMUTABLE)

name = "Python"

print(type(name))  # <class 'str'>

# ------------------------------------------------
# 2.6 NoneType
# ------------------------------------------------
# Represents absence of value

x = None

print(type(x))  # <class 'NoneType'>

# ================================================
# 3. COLLECTION DATA TYPES
# ================================================

# ------------------------------------------------
# 3.1 list (Ordered, Mutable), index starts from 0
# ------------------------------------------------
# - Can change after creation
# - Allows duplicates
# - Maintains insertion order

nums = [1, 2, 3, "jay"]
nums[0] = 100

print(nums)  # [100, 2, 3, "jay"]


# ------------------------------------------------
# 3.2 tuple (Ordered, Immutable)
# ------------------------------------------------
# - Cannot be changed after creation
# - Faster than lists
# - Used for fixed data

coords = (10, 20)

# coords[0] = 5  ❌ ERROR

# ------------------------------------------------
# 3.3 set (Unordered, Unique, Mutable)
# ------------------------------------------------
# - No duplicates
# - No guaranteed order

unique_nums = {1, 2, 2, 3}

print(unique_nums)  # {1, 2, 3}

# More example of set mutation

x = {5, 6, 7}
print(x) # {5, 6, 7}

x.add(8)
print(x) # {8, 5, 6, 7}
x.add(5) # ignore
print(x) # {8, 5, 6, 7}

# ------------------------------------------------
# 3.4 dict (Key–Value Mapping, mutable)
# ------------------------------------------------
# - Keys must be unique
# - Values can be anything

student = {
    "name": "Jay",
    "age": 29
}

print(student["name"])  # Jay

# more example of dict mutation

student["std"] = 8

print(student) # {'name': 'Jay', 'age': 29, 'std': 8}

student["name"] = "vishal"

print(student) # {'name': 'Jay', 'age': 29, 'std': 8}

# ================================================
# 4. TYPE CHECKING
# ================================================

# ------------------------------------------------
# 4.1 type()
# ------------------------------------------------

x = 10
y = "Python"
z = [1, 2, 3]

print(type(x))  # int
print(type(y))  # str
print(type(z))  # list

# ================================================
# 5. MUTABILITY vs IMMUTABILITY (CRITICAL)
# ================================================

# ------------------------------------------------
# 5.1 Immutable Types
# ------------------------------------------------
# Immutable objects CANNOT be changed in place.

# Examples:
# - int
# - float
# - bool
# - str
# - tuple

# Example:
x = 10
x = x + 1

# Explanation:
# - Original 10 is NOT changed
# - New object 11 is created
# - x now refers to 11

# ------------------------------------------------
# 5.2 Mutable Types
# ------------------------------------------------
# Mutable objects CAN be changed in place.

# Examples:
# - list
# - dict
# - set

# Example:
nums = [1, 2, 3]
nums.append(4)

print(nums)  # [1, 2, 3, 4]

# Explanation:
# - Same list object is modified
# - Memory reference remains the same

# ================================================
# 6. MEMORY REFERENCE BEHAVIOR
# ================================================

# ------------------------------------------------
# 6.1 Immutable Reference Example
# ------------------------------------------------
a = 10
b = a

a = 20

print(a)  # 20
print(b)  # 10

# ------------------------------------------------
# 6.2 Mutable Reference Example (IMPORTANT)
# ------------------------------------------------
list1 = [1, 2, 3]
list2 = list1

list1.append(4)

print(list1)  # [1, 2, 3, 4]
print(list2)  # [1, 2, 3, 4]

# Explanation:
# - list1 and list2 refer to the SAME object
# - Change via one reference affects the other

# ================================================
# 7. SHALLOW UNDERSTANDING OF REFERENCES
# ================================================

# Key idea:
# - Assignment copies the REFERENCE, not the object
# - Especially dangerous with mutable objects

# Safe copy (list):

original = [1, 2, 3]
copy = original.copy()

copy.append(4)

print(original)  # [1, 2, 3]
print(copy)      # [1, 2, 3, 4]

# ================================================
# SUMMARY
# ================================================

# ✔ Everything in Python is an object  
# ✔ Variables are references, not containers  
# ✔ Python is dynamically typed  
# ✔ Mutable objects change in place  
# ✔ Immutable objects create new objects  
# ✔ Assignment copies references, not values  

# ================================================
# END OF NOTES
# ================================================











pairs = [('name', 'Alice'), ('age', 25), ('location', 'New York')]
student = dict(pairs)

print(student)