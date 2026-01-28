# ================================================
# 1. LIST OPERATIONS (ORDERED, MUTABLE), indices starts from '0'
# ================================================

# Lists are:
# - Ordered
# - Mutable
# - Allow duplicates
# - Most commonly used collection

# ------------------------------------------------
# 1.1 Creating a List
# ------------------------------------------------
nums = [1, 2, 3]

# ------------------------------------------------
# 1.2 Accessing Elements
# ------------------------------------------------
nums = [10, 20, 30]

print(nums[0])   # 10
print(nums[-1])  # 30

# ------------------------------------------------
# 1.3 Modifying Elements (MUTATES)
# ------------------------------------------------
nums[1] = 200
print(nums)  # [10, 200, 30]

# ------------------------------------------------
# 1.4 append() – Add ONE element (MUTATES) at the end
# ------------------------------------------------
nums = [1, 2]
nums.append(3)

print(nums)  # [1, 2, 3]

# ------------------------------------------------
# 1.5 extend() – Add MULTIPLE elements (MUTATES) at the end
# ------------------------------------------------
nums = [1, 2]
nums.extend([3, 4])

print(nums)  # [1, 2, 3, 4]

# ------------------------------------------------
# 1.6 insert() – Add at specific index (MUTATES)
# ------------------------------------------------
my_list = [10, 20, 30, 40]

# Insert 5 at index 2 (between 20 and 30)
my_list.insert(2, 5)

print(my_list)
# Output: [10, 20, 5, 30, 40]

# insert at biginning

my_list = ['b', 'c', 'd']

# Insert 'a' at index 0
my_list.insert(0, 'a')

print(my_list)
# Output: ['a', 'b', 'c', 'd']

# insert at the end (much better way is using append and extend method..
# this is just to see using insert... so here we need to use index greater than or equal to the current length of the list. )

my_list = [1, 2, 3]

# The length of the list is 3.

# This will place the element at the end of the list.
my_list.insert(100, 4)

print(my_list)

# Output: [1, 2, 3, 4]

# ------------------------------------------------
# 1.7 remove() – Remove by VALUE (MUTATES)
# ------------------------------------------------
nums = [1, 2, 3]
nums.remove(2)

print(nums)  # [1, 3]

# ------------------------------------------------
# 1.8 pop() – Remove by INDEX (MUTATES) and returns the popped element
# ------------------------------------------------
nums = [1, 2, 3]
x = nums.pop()

print(x)     # 3
print(nums)  # [1, 2]

my_list = ['apple', 'banana', 'cherry', 'date', 'elderberry']
# Index values:    0        1         2       3         4

# Pop the element at index 2 ('cherry')
removed_element = my_list.pop(2)

print(f"Removed element: {removed_element}")
print(f"List after popping: {my_list}")

# ------------------------------------------------
# 1.9 del – Delete by index or slice (MUTATES), simply removes but does not return
# ------------------------------------------------
nums = [1, 2, 3, 4]
del nums[1]

print(nums)  # [1, 3, 4]

# ------------------------------------------------
# 1.10 clear() – Remove ALL elements
# ------------------------------------------------
nums = [1, 2]
nums.clear()

print(nums)  # []

# ------------------------------------------------
# 1.11 copy() – Shallow Copy (IMPORTANT)
# ------------------------------------------------
a = [1, 2]
b = a.copy()

b.append(3)

print(a)  # [1, 2]
print(b)  # [1, 2, 3]

# ------------------------------------------------
# 1.12 Sorting
# ------------------------------------------------
nums = [3, 1, 2]

nums.sort()          # MUTATES the original array
print(nums)          # [1, 2, 3]

nums = [3, 1, 2]
sorted_nums = sorted(nums)  # NON-MUTATING

print(sorted_nums)  # [1, 2, 3]
print(nums)         # [3, 1, 2]

# Customizing the Sort Order

# 1. reverse=True: Sorts the list in descending order (Z to A).

my_list = ["banana", "apple", "cherry", "date"]
my_list.sort(reverse=True)
print(my_list)
# Output: ['date', 'cherry', 'banana', 'apple']

# 2. Case-insensitive sorting: Use key=str.lower to treat uppercase and lowercase letters the same.
# otherwise the string with Caps will come first then the lower one

my_list = ["Banana", "apple", "Grape", "pear"]
my_list.sort(key=str.lower)
print(my_list)
# Output: ['apple', 'Banana', 'Grape', 'pear']

# 3. Sort by length: Use key=len to sort strings by their length

my_list = ["apple", "kiwi", "banana", "cherry"]
my_list.sort(key=len)
print(my_list)
# Output: ['kiwi', 'apple', 'cherry', 'banana']

# 4. Sort numeric strings numerically: If your list contains strings that are actually numbers,
# use key=int or key=float to sort them based on their numerical value instead of lexicographical order.

num_strings = ["10", "2", "30", "4"]
num_strings.sort(key=int)
print(num_strings)
# Output: ['2', '4', '10', '30']

# ------------------------------------------------
# 1.14 Other Useful List Operations
# ------------------------------------------------
len(nums)
min(nums)
max(nums)
sum(nums) # sum of all elements in list
nums.count(2) # how many times 2 appers in list
nums.index(3) # index of element 3 in list (index in list start from 0)

print("nums array: ",nums)
nums.reverse() # reverse the list and mutates original list
print("reversed array: ", nums) 

nums.reversed() # reverse the list but non mutating
