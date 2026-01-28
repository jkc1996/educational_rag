# ================================================
# STRING OPERATIONS & METHODS IN PYTHON
# ================================================

# Strings are:
# - Ordered
# - Immutable (cannot be changed in place)
# - Sequence of characters
# - Very heavily used in real-world applications

# ================================================
# 1. CREATING STRINGS
# ================================================

s1 = "Python"
s2 = 'Programming'
s3 = """Multi
Line
String"""

print(s1)
print(s2)
print(s3)

# ================================================
# 2. ACCESSING CHARACTERS (INDEXING)
# ================================================

text = "Python"

print(text[0])    # P
print(text[-1])   # n

# ================================================
# 3. STRING SLICING
# ================================================

text = "PythonProgramming"

print(text[0:6])     # Python
print(text[6:])      # Programming
print(text[:6])      # Python
print(text[::2])     # PtoPormig
print(text[::-1])    # Reverse string

# ================================================
# 4. STRING IMMUTABILITY
# ================================================

name = "Python"

# name[0] = "J"   ❌ ERROR: strings are immutable

name = "Jython"     # Creates a NEW string
print(name)

# ================================================
# 5. CHANGING CASE
# ================================================

text = "PyThOn"

print(text.lower())   # python
print(text.upper())   # PYTHON
print(text.title())   # Python
print(text.capitalize())  # Python
print(text.swapcase())     # pYtHoN

# ================================================
# 6. TRIMMING WHITESPACE
# ================================================

text = "   hello world   "

print(text.strip())    # Both sides
print(text.lstrip())   # Left side
print(text.rstrip())   # Right side

# ================================================
# 7. SEARCHING IN STRINGS
# ================================================

text = "python programming"

print(text.find("python"))     # 0
print(text.find("java"))       # -1 (NOT FOUND)

print(text.index("python"))    # 0
# text.index("java")           # ❌ ERROR if not found

# ================================================
# 8. CHECKING STRING CONTENT
# ================================================

text = "Python123"

print(text.isalpha())   # False
print(text.isdigit())   # False
print(text.isalnum())   # True
print(text.islower())   # False
print(text.isupper())   # False

# ================================================
# 9. STARTS WITH / ENDS WITH
# ================================================

filename = "data.csv"

print(filename.startswith("data"))  # True
print(filename.endswith(".csv"))    # True

# ================================================
# 10. REPLACE TEXT
# ================================================

text = "I like Java"

new_text = text.replace("Java", "Python")
print(new_text)

# ================================================
# 11. SPLIT & JOIN (VERY IMPORTANT)
# ================================================

text = "apple,banana,orange"

parts = text.split(",")
print(parts)

joined = "-".join(parts)
print(joined)

# ================================================
# 12. COUNT OCCURRENCES
# ================================================

text = "banana"

print(text.count("a"))   # 3

# ================================================
# 13. STRING FORMATTING
# ================================================

name = "Jay"
age = 29

# f-string (RECOMMENDED)
print(f"My name is {name} and I am {age} years old")

# format()
print("My name is {} and I am {} years old".format(name, age))

# ================================================
# 14. ESCAPE CHARACTERS
# ================================================

print("Hello\nWorld")   # New line
print("Hello\tWorld")   # Tab
print("He said \"Hi\"") # Quotes

# ================================================
# 15. MEMBERSHIP TESTING
# ================================================

text = "Python Programming"

print("Python" in text)     # True
print("Java" not in text)   # True

# ================================================
# 16. STRING COMPARISON
# ================================================

print("apple" == "apple")   # True
print("apple" < "banana")  # True (lexicographical)

# ================================================
# 17. CONVERTING OTHER TYPES TO STRING
# ================================================

num = 100
pi = 3.14

print(str(num))
print(str(pi))

# ================================================
# 18. REAL-WORLD EXAMPLE: CLEAN USER INPUT
# ================================================

raw_email = "  USER@Example.Com  "

clean_email = raw_email.strip().lower()
print(clean_email)

# ================================================
# SUMMARY
# ================================================

# ✔ Strings are immutable
# ✔ Support indexing & slicing
# ✔ Rich built-in methods
# ✔ split() & join() are heavily used
# ✔ f-strings are best for formatting
# ✔ Used extensively in file handling & Pandas

# ================================================
# END OF STRING OPERATIONS
# ================================================
