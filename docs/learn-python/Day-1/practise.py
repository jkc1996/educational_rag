# problem statement - 1:
# Write a Python program to:

# Count how many times each word appears

# Print only the words that appear more than once

text = "Python is fun and Python makes coding fun"

text_dict = {}

text_list = text.split()

final_result = []

print(text_list)

for word in text_list:
  if word not in text_dict:
    text_dict[word] = 1

  else:
    text_dict[word] += 1

# instead of above if else we could write - text_dict[word] = text_dict.get(word, 0) + 1

for key, value in text_dict.items():
  if value > 1:
    final_result.append(key)

print (final_result)

#---------------------------------------------------------------------------------------

# problem statement - 2:

# Write a Python program to:

# Find numbers that appear more than once

# Store them in a new list without duplicates


nums = [4, 7, 2, 7, 4, 9, 2, 1]

nums_dict = {}

final_num_result = []

for num in nums:
  nums_dict[num] = nums_dict.get(num, 0) + 1

for key, value in nums_dict.items():
  if value > 1:
    final_num_result.append(key)

print (final_num_result)

# let say we want number with highest frequncy

sorted_by_values = dict(sorted(nums_dict.items(), key=lambda item: item[1], reverse=True))
print(sorted_by_values)

print(sorted_by_values.keys()) # this will be of type dict_keys

print(list(sorted_by_values.keys())[0]) # converting into the normal list and accessing element at index 0, which is the having highest freqency

#-------------------------------------------------------------------------------------------

# problem statement - 3:  

# Write a Python program to:

# Create a new list containing numbers that appear only once

# Preserve the original order

nums = [5, 3, 8, 3, 5, 9, 1]

nums_dict = {}

final_num_result = []

for num in nums:
  nums_dict[num] = nums_dict.get(num, 0) + 1

for key, value in nums_dict.items():
  if value == 1:
    final_num_result.append(key)

print (final_num_result)

#------------------------------------------------------------------------------------------

# Problem statement - 4: 

# Find two numbers whose sum equals the target, and print them.

nums = [2, 7, 11, 15]
target = 9

# my solution:

nums = [2, 7, 11, 15]
target = 9

resultant_pair_list = []

for i in nums:
  for j in nums:
    if i + j == target:
      if (j, i) not in resultant_pair_list:
        resultant_pair_list.append((i, j))

print(resultant_pair_list)

# but optimized one - As we loop, check if target - current_number already exists.

seen = set()

for num in nums:
    needed = target - num
    if needed in seen:
        print((needed, num))
    seen.add(num)

# --------------------------------------------------------------------------------------

# Problem statement - 5:

# text = "aabbbccccdd"

# Write a Python program to compress the string so it becomes: a2b3c4d2


text = "aabbbccccdda"

char_dict = {}
final_str = ''

for char in text:
  char_dict[char] = char_dict.get(char, 0) + 1

for key, value in char_dict.items():
  final_str += key + str(value)

print(final_str)

# --------------------------------------------------------------------------------------

# Problem statement - 6

# Write a Python program to create a new list of alternating sum like:

# [1-2, 3-4, 5-6]  →  [-1, -1, -1]

nums = [1, 2, 3, 4, 5, 6]

# my solution(solution 1):

nums = [1, 2, 3, 4, 5, 6]

final_minus_list = []

odd = nums[::2]
even = nums[1::2]

print(odd)
print(even)

for i, odd_value in enumerate(odd):
  for j, even_value in enumerate(even):
    if i == j:
      final_minus_list.append(odd_value - even_value)
      break

print(final_minus_list)

# gpt optimized solution - 1(just one loop)(solution 2):
nums = [1, 2, 3, 4, 5, 6]

odd = nums[::2]
even = nums[1::2]

final_minus_list = []

for i in range(len(odd)):
    final_minus_list.append(odd[i] - even[i])

print(final_minus_list)

# (solution 3)but below one is optimized one where we used zip, which makes the pair index wise and make a tuple of pair

final_minus_list = []

for a, b in zip(nums[::2], nums[1::2]):
    final_minus_list.append(a - b)

print(final_minus_list)

# -------------------------------------------------------------------------------------------------------------

# Problem statement - 7

# Write a Python program to create a new string that keeps only the first occurrence of each character, in the same order.

text = "abcdaefbg"

text = "abcdaefbg"

seen = {} # when we see char first time then only push in this dict
result = ""

for char in text:
  if char not in seen:
    seen[char] = 1 # here 1 is just dummy value.. we can put anyting.. the reason here is that since its dict, we need to push key(char) and value (anythign, we mentioned 1)
    result += char # for smaller loop += is good, but for large loop we can do - result = "".join(chars)

print(result)

# ----------------------------------------------------------------------------------------------------------

# Problem statement - 8

# Write a Python program to rotate the list to the right by k positions.

# expected output - [40, 50, 10, 20, 30], if k = 3 then - [30, 40, 50, 10, 20]

nums = [10, 20, 30, 40, 50]
k = 2


nums = [10, 20, 30, 40, 50]
k = 2

def rotate_list_right(num_list, k):
  part_1 = num_list[:len(num_list) - k]
  part_2 = num_list[len(num_list) - k:]
  return part_2 + part_1 # here we can use .extend too - part_2.extend(part_1) or we can write part_1 += part_2

print(rotate_list_right(nums, k))

# ------------------------------------------------------------------------------------------------------

# Problem statement - 9
# Write a Python program to: Separate letters and numbers Return output as:

# letters = "abcde"
# numbers = "12345"

# just for knowledge isinstance(x, int) check if x is instance of int

text = "a1b2c3d4e5"

str_list = []
num_list = []

for char in text:
  if char.isdigit():
    num_list.append(char)
  else:
    str_list.append(char)

print("".join(str_list), "".join(num_list))

# --------------------------------------------------------------------------------------------------

# Problem: Invert and Group
# You are given a dictionary where the keys are student names and the values are the subjects they study. Your task is to invert this mapping so that the keys are the subjects and the values are a list of students studying that subject.

# Constraint: The list of students for each subject must be sorted alphabetically.

# Expected output:
# {
#     'Math': ['Alice', 'Charlie', 'Frank'], 
#     'Science': ['Bob', 'Eve'], 
#     'History': ['David']
# }

students = {
    'Alice': 'Math',
    'Bob': 'Science',
    'Charlie': 'Math',
    'David': 'History',
    'Eve': 'Science',
    'Frank': 'Math'
}

# my solution: O(N*N) complexity
unique_subject = list(set(students.values()))

subject_dict = {}

for subject in unique_subject:
  student_list = []
  for key, value in students.items():
    if subject == value:
      student_list.append(key)

  # Requirement: The list must be sorted
  student_list.sort()
    
  # Now assign the populated list to the dictionary
  subject_dict[subject] = student_list

print(subject_dict)

# gemini solution: O(N) complexity

inverted = {}

for student, subject in students.items():
    # If subject doesn't exist, create empty list. Then append student.
    inverted.setdefault(subject, []).append(student)

# Apply the sorting constraint at the end
for subject in inverted:
    inverted[subject].sort()

print(inverted)


# -------------------------------------------------------------------------------------------------

# Problem: String Expansion Input: s = "a3b12c2" Expected Output: aaabbbbbbbbbbbbcc

# (Remember: The number of digits following a character can be more than 1, like the '12' after 'b').

s = "a3b12c2"

output = ""
current_letter = ""
num = ""

for char in s:
    if char.isalpha():
        # If there was a previous letter waiting, process it now.. this like when we reach to b we need to process 'a' and '3' from previous iterations then only set the new char as 'b' and reset then num as '' for 'b'
        if current_letter != "":
            output += current_letter * int(num)
        
        # Now set the new letter as the "current" one waiting
        current_letter = char
        num = "" # Reset the number builder
        
    elif char.isdigit():
        num += char

# CRITICAL: The loop finishes after '2', so the last batch (c, 2) 
# hasn't been added to output yet. We do it manually here.
output += current_letter * int(num)

print(output)

# --------------------------------------------------------------------------------------------------

# Problem: The Gradebook You have two lists: one containing student names and one containing their scores. You need to combine them into a dictionary, but exclude anyone who scored below 50.

# Constraint: Try to do this without using a counter variable (like i = 0).

# Input:
# names = ["Alice", "Bob", "Charlie", "David"]
# scores = [85, 42, 78, 90]

# Expected Output:
# {'Alice': 85, 'Charlie': 78, 'David': 90}

names = ["Alice", "Bob", "Charlie", "David"]
scores = [85, 42, 78, 90]

final_dict = {}

for name, score in zip(names, scores):
    # Only add to dictionary if the condition is met
    if score >= 50:
        final_dict[name] = score

print(final_dict)

# --------------------------------------------------------------------------------------------------------

# Problem:You are given a list of visitor IDs. Every visitor appears exactly twice, except for one visitor who appears only once. You need to find that unique visitor ID.Constraint: Try to solve this without using a nested loop (which would be $O(N^2)$). A dictionary or set approach is $O(N)$.Input:Pythonids = [101, 202, 101, 303, 202, 404, 303]
# Expected Output: 404
# (Note: 101, 202, and 303 all appear twice. 404 is the only one appearing once).
# Hint: Think about how you might count them, or if there is a math trick involving sum() and set().

ids = [101, 202, 101, 303, 202, 404, 303]

ids_dict = {}

for identity in ids:
  ids_dict[identity] = ids_dict.get(identity, 0) + 1

print(ids_dict)

for key, value in ids_dict.items():
  if value == 1:
    print(key)


# approach 2(using set and sum):

# logic:

# If every number appeared twice, the sum of the list would be exactly double the sum of the unique numbers.

# Since one number appears only once, the sum of the list will be a little bit short.

# The Formula: 2 X sum(unique_elements) - sum(all_elements) = unique_visitor

# 2 * (101+202+303+404) - (101+202+101+303+202+404+303)
unique_visitor = 2 * sum(set(ids)) - sum(ids)

print(unique_visitor)

# -------------------------------------------------------------------------------------------------

# Problem: find absent employees and do the sorting also (sorted converted set into sorted list also)

all_employees = ["Alice", "Bob", "Charlie", "David", "Eve"]
present_employees = ["Bob", "Eve", "Alice"]

absent_employee = set(all_employees) - set(present_employees)
print(sorted(absent_employee))

# ------------------------------------------------------------------------------------------------

# New Problem: Merge and Sum

# You have two dictionaries representing inventory counts from two different warehouses. You need to merge them into a single total inventory dictionary.

# The Rule:

# If an item exists in both dictionaries, sum their values.

# If an item exists in only one, keep its value as is.

# Constraint: Try to solve this without using collections.Counter (which makes it too easy). Use standard dictionary loops or methods.

# Expected Output:

# {'apples': 10, 'bananas': 35, 'oranges': 15, 'pears': 30}


w1 = {'apples': 10, 'bananas': 20, 'oranges': 5}
w2 = {'bananas': 15, 'oranges': 10, 'pears': 30}

# Your logic to get all unique keys (this works!)
# A shortcut for this is: unique_items = set(w1) | set(w2)
unique_items = list(set(w1.keys()) | set(w2.keys())) 

final = {}

for item in unique_items:
    # "get(item, 0)" means: Give me the value, or 0 if it doesn't exist.
    # This handles "apples" (10 + 0), "bananas" (20 + 15), and "pears" (0 + 30) automatically.
    final[item] = w1.get(item, 0) + w2.get(item, 0)

print(final)

# ---------------------------------------------------------------------------------------------------

# anagram problem:

word_list = ["eat", "tea", "tan", "ate", "nat", "bat"]

anagrams = {}

for word in word_list:
    # 1. Create the "Fingerprint"
    # sorted('eat') gives ['a', 'e', 't']. 
    # "".join(...) turns it back into the string "aet"
    # We do this because Lists cannot be dictionary keys, but Strings can.
    sorted_key = "".join(sorted(word))
    
    # 2. Group them using setdefault (or your if/else logic)
    # If "aet" is not in dict, create empty list, then append "eat"
    anagrams.setdefault(sorted_key, []).append(word)

    # below 3 lines are using if else logic
    # if sorted_key not in anagrams:
    #   anagrams[sorted_key] = []
    # anagrams[sorted_key].append(word)
    
# We only want the groups (the values), not the keys like 'aet'
print(list(anagrams.values()))

#-----------------------------------------------------------------------------------------------------

# meaning of this line: anagrams.setdefault(sorted_key, []).append(word)

# The function checks if sorted_key exists.

# If NO: It creates the key with an empty list [] as the value, returns that new list, and then appends the word to it.

# If YES: It retrieves the existing list, and then appends the word to it.

# ------------------------------------------------------------------------------------------------------

# Problem: Palindrome Cleaner Check if a string is a palindrome (reads the same forward and backward). You must ignore spaces and capitalization.

s = "Race Car"

# 1. Clean the string first (store it in a variable to keep it readable)
cleaned = s.lower().replace(" ", "")

# 2. Compare cleaned vs cleaned-reversed
print(cleaned == cleaned[::-1])

# -------------------------------------------------------------------------------------------------------

# New Problem: The missing number.
# Problem: You are given a list containing distinct numbers taken from the range 0, 1, 2, ..., n.
# However, one number from the sequence is missing. Find that missing number.
# (Hint: Think about Sum again. What is the sum of 0 to n ?)
# Input = [3, 0, 1]
# (Here n=3, so the full range should be 0, 1, 2, 3. The missing number is 2)
# Input 2 = [0, 1]
# (Here n=2, full range is 0, 1, 2. Missing is 2).Expected Output: 2

# Hint:
# The sum of numbers from 0 to n is given by the formula n(n+1)/2. Or you can just sum the range!

nums = [3, 0, 1]

print("missing number: ", sum(range(len(nums) + 1)) - sum(nums))

# ----------------------------------------------------------------------------------------------------

# Problem: Given a list of numbers, move all 0s to the end of the list while maintaining the relative order of the non-zero elements.

# Constraint: Try to solve this without creating a copy of the list if possible (in-place), or just find the cleanest logic you can.


nums = [0, 1, 0, 3, 12]

# 1. Count them first!
zeros_count = nums.count(0)

# 2. Remove them (using your safe copy logic) because if we do .remove on original array then it will change the index shift 
for num in nums[:]:
    if num == 0:
        nums.remove(num)

# 3. Add them back to the end
# [0] * 2 becomes [0, 0]. "extend" adds the list items to the end.
nums.extend([0] * zeros_count)

print(nums)

# solutin in pro way:

# 1. Gather all non-zeros
non_zeros = [n for n in nums if n != 0]

# 2. Count how many zeros we need
count_zeros = len(nums) - len(non_zeros)

# 3. Glue them together
result = non_zeros + ([0] * count_zeros)

print(result)

# ----------------------------------------------------------------------------------------------------

# Problem: Find the first character in a string that appears only once. 

# Input: s = "swiss" Output: 'w'

# Hint:

# Loop 1: Count how many times every letter appears (store in a dict).

# Loop 2: Go through the string again. The first letter you see that has a count of 1 is your winner.

s = 'swiss'
char_dict = {}

# 1. Count (This was perfect)
for char in s:
    char_dict[char] = char_dict.get(char, 0) + 1

# 2. Check (The Fix)
for char in s:
    # We check the count for the CURRENT character in the loop
    if char_dict[char] == 1:
        print(char)
        break  # We found the first one, so we stop!

# ----------------------------------------------------------------------------------------------

# Problem: find second largest without set and sorting

nums = [10, 20, 4, 45, 99]

# Start with very small numbers or may be -1
largest = float('-inf')
second = float('-inf')

for num in nums:
    if num > largest:
        # The King is dethroned! He becomes the Prince.
        second = largest
        largest = num
    elif num > second and num != largest:
        # Not bigger than King, but beats the Prince.
        second = num

print("Largest:", largest)
print("Second:", second)

# ------------------------------------------------------------------------------------------

# New Problem: Flatten the Matrix
# This tests your nested loop skills.

# Problem: You are given a 2D list (a list of lists). You need to flatten it into a single 1D list.

# Input:

matrix = [
    [1, 2, 3],
    [4, 5],
    [6, 7, 8, 9]
]

flatten_list = []

for row in matrix:
    for item in row:
        flatten_list.append(item)

print(flatten_list)

# solution using list comprihansion:

#  <Result>      <1. Outer Loop>     <2. Inner Loop>
# [   item       for row in matrix   for item in row   ]

flatten_list = [item for row in matrix for item in row]
print(flatten_list)

# --------------------------------------------------------------------------------

# New Problem: Valid Parentheses (Logic Check)
# This problem tests your ability to handle "State" while looping.

# Problem: You are given a string containing only parentheses ( and ). You need to determine if the string is "valid". A string is valid if:

# Every opening parenthesis ( has a matching closing parenthesis ).

# They are closed in the correct order (you can't close a parenthesis that hasn't been opened yet).

# Hint:Imagine walking through the string.

# if you See "(": Add 1 to your balance.
# if you See ")": Subtract 1 from your balance.
# Critical Check: If the balance ever drops below 0, what does that mean?

s = "(()())("

balance = 0
is_valid = True 

for char in s:
    if char == '(':
        balance += 1
    else:
        balance -= 1
    
    # 1. CRITICAL: Check immediately if we dipped below zero
    if balance < 0:
        is_valid = False
        break

# 2. FINAL: If we are still valid, check if any were left open (balance must be 0)
if is_valid and balance == 0:
    print(True)
else:
    print(False)

# ------------------------------------------------------------------------------------------------------

# Problem: find unique elements in 2

list1 = [1, 2, 2, 1, 3]
list2 = [2, 2, 3, 4]

unique_element = set(list1) & set(list2)

print(list(unique_element))

# ---------------------------------------------------------------------------------------------------

# New Problem: Running Sum

# Problem:Given a list of numbers, return a list where each element is the running sum of the previous elements.
# Index 0: nums[0]
# Index 1: nums[0] + nums[1]
# Index 2: nums[0] + nums[1] + nums[2]
# Input = [1, 2, 3, 4]
# Expected Output: [1, 3, 6, 10]
# (Explanation: [1, 1+2, 1+2+3, 1+2+3+4])

nums = [1, 2, 3, 4]
running_sum = []
current_total = 0

for num in nums:
    current_total += num      # Update the running total
    running_sum.append(current_total) # Save it

print(running_sum)

# -------------------------------------------------------------------------------------------------------------

# New Problem: Grouping by Parity (Odd/Even)

# This problem tests your ability to organize data into specific buckets.

# Problem: Given a list of integers, create a dictionary with two keys: 'even' and 'odd'. The values should be lists of the corresponding numbers.

# Input:

# nums = [1, 2, 3, 4, 5, 6, 7]

# Expected Output:

# {
#     'odd': [1, 3, 5, 7], 
#     'even': [2, 4, 6]
# }

# Constraint: Initialize your dictionary before the loop so you don't have to check if the keys exist inside the loop.

nums = [1, 2, 3, 4, 5, 6, 7]

group_dict = {}

for num in nums:
  if num % 2 == 0:
    group_dict.setdefault('even', []).append(num)
  else:
    group_dict.setdefault('odd', []).append(num)

print(group_dict)

# OR 

nums = [1, 2, 3, 4, 5, 6, 7]

# Initialize buckets beforehand
group_dict = {'odd': [], 'even': []}

for num in nums:
    if num % 2 == 0:
        group_dict['even'].append(num)
    else: # <--- The critical fix
        group_dict['odd'].append(num)

print(group_dict)

# -----------------------------------------------------------------------------------------------------

# New Problem: The Majority Element
# This is a very famous interview problem.

# Problem: Given a list of size n, find the majority element. The majority element is the element that appears more than n / 2 times.

# Input:

# nums = [2, 2, 1, 1, 1, 2, 2]
# (Length is 7. Half is 3.5. The number 2 appears 4 times, so it wins).

# Input 2:

# nums = [3, 2, 3]

nums = [2, 2, 1, 1, 1, 2, 2]

num_freq = {}

for num in nums:
  num_freq[num] = num_freq.get(num, 0) + 1

print(num_freq)

for key, value in num_freq.items():
  if value > len(nums)/2:
    print(key)
    break

# --------------------------------------------------------------------------------------------

# Problem: Reverse Words in a String Given a string s, reverse the order of the words.

# The words should be separated by a single space.

# Your result should not contain leading or trailing spaces.

s = "  the sky is  blue  "

# 1. Split (handles multiple spaces automatically) -> ['the', 'sky', 'is', 'blue']
# 2. Reverse -> ['blue', 'is', 'sky', 'the']
# 3. Join with a space
print(" ".join(reversed(s.split())))