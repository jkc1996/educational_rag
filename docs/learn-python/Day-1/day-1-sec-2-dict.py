# ================================================
# 4. DICTIONARY OPERATIONS (KEY–VALUE MAPPING)
# ================================================

# Dictionaries are:
# - Key–value data structures
# - Mutable
# - Keys must be UNIQUE and IMMUTABLE
# - Values can be any data type
# - Insertion-ordered (Python 3.7+)

# ------------------------------------------------
# 4.1 Creating a Dictionary
# ------------------------------------------------

student = {
    "name": "Jay",
    "age": 29,
    "city": "Mumbai"
}

print(student)

# Creating using dict() constructor
employee = dict(id=101, role="Engineer")
print(employee)

# ------------------------------------------------
# 4.2 Accessing Values
# ------------------------------------------------

print(student["name"])        # Direct access (ERROR if key missing)
print(student.get("age"))     # Safe access
print(student.get("salary"))  # None (no error)

# Providing default value with get()
print(student.get("salary", 0))

# ------------------------------------------------
# 4.3 Adding & Modifying Entries
# ------------------------------------------------

student["age"] = 30           # Modify existing key
student["email"] = "jay@mail.com"  # Add new key

print(student)

# ------------------------------------------------
# 4.4 Removing Entries
# ------------------------------------------------

# pop() – Removes key and RETURNS its value
age = student.pop("age")
print(age)
print(student)

# del – Removes key (NO return)
del student["city"]
print(student)

# popitem() – Removes LAST inserted key-value pair
last_item = student.popitem()
print(last_item)
print(student)

# clear() – Removes ALL key-value pairs
student.clear()
print(student)

# ------------------------------------------------
# 4.5 Checking Keys & Length
# ------------------------------------------------

data = {"a": 1, "b": 2}

print("a" in data)      # True
print("x" in data)      # False
print(len(data))        # 2

# ------------------------------------------------
# 4.6 Looping Through Dictionary
# ------------------------------------------------

user = {"name": "Jay", "age": 29}

# Loop through keys (default)
for key in user:
    print(key)

# Loop through values
for value in user.values():
    print(value)

# Loop through key-value pairs
for key, value in user.items():
    print(key, value)

# ------------------------------------------------
# 4.7 keys(), values(), items()
# ------------------------------------------------

print(user.keys())     # dict_keys object
print(user.values())   # dict_values object
print(user.items())    # dict_items object

# ------------------------------------------------
# 4.8 copy() – Shallow Copy
# ------------------------------------------------

original = {"x": 1, "y": 2}
copy_dict = original.copy()

copy_dict["x"] = 100

print(original)
print(copy_dict)

# ------------------------------------------------
# 4.9 update() – Merge Dictionaries
# ------------------------------------------------

a = {"x": 1, "y": 2}
b = {"y": 99, "z": 3}

a.update(b)
print(a)   # {'x': 1, 'y': 99, 'z': 3}

# ------------------------------------------------
# 4.10 Dictionary with Mutable Values (IMPORTANT)
# ------------------------------------------------

student = {
    "name": "Jay",
    "skills": ["Python", "JS"]
}

student["skills"].append("SQL")
print(student)

# ------------------------------------------------
# 4.11 Nested Dictionaries
# ------------------------------------------------

company = {
    "emp1": {"name": "Amit", "age": 30},
    "emp2": {"name": "Neha", "age": 28}
}

print(company["emp1"]["name"])  # Amit

# ------------------------------------------------
# 4.12 Dictionary Comprehension
# ------------------------------------------------

squares = {x: x * x for x in range(5)}
print(squares)

# ------------------------------------------------
# 4.13 Using Tuples as Dictionary Keys
# ------------------------------------------------

locations = {
    (10, 20): "Point A",
    (30, 40): "Point B"
}

print(locations[(10, 20)])

# ------------------------------------------------
# 4.14 setdefault() – Insert if Missing
# ------------------------------------------------

data = {"a": 1}

data.setdefault("b", 2)
data.setdefault("a", 100)  # Will NOT overwrite existing key

print(data)

# ------------------------------------------------
# 4.15 fromkeys() – Create Dictionary from Keys
# ------------------------------------------------

keys = ["id", "name", "email"]

default_dict = dict.fromkeys(keys, None)
print(default_dict)

# ------------------------------------------------
# 4.16 Sorting Dictionary (By Keys or Values)
# ------------------------------------------------

scores = {"bob": 85, "alice": 95, "charlie": 90}

# Sort by keys
sorted_by_keys = dict(sorted(scores.items()))
print(sorted_by_keys)

# Sort by values
sorted_by_values = dict(sorted(scores.items(), key=lambda item: item[1]))
print(sorted_by_values)

# ------------------------------------------------
# 4.17 Real-World Example: Counting Frequency
# ------------------------------------------------

text = "banana"
freq = {}

for char in text:
    freq[char] = freq.get(char, 0) + 1

print(freq)

# ================================================
# END OF DICTIONARY OPERATIONS
# ================================================
