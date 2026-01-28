# ================================================
# 5. CONTROL STATEMENTS IN PYTHON
# ================================================

# Control statements control the FLOW of execution
# based on conditions, repetition, or early exit.

# Python control statements include:
# - if / elif / else
# - match-case (Python 3.10+)
# - for loop
# - while loop
# - break, continue, pass

# ================================================
# 5.1 IF STATEMENT
# ================================================

# if executes a block ONLY if condition is True

age = 20

if age >= 18:
    print("Adult")

# ================================================
# 5.2 IF – ELSE
# ================================================

age = 15

if age >= 18:
    print("Adult")
else:
    print("Minor")

# ================================================
# 5.3 IF – ELIF – ELSE
# ================================================

marks = 75

if marks >= 90:
    print("Grade A")
elif marks >= 75:
    print("Grade B")
elif marks >= 60:
    print("Grade C")
else:
    print("Fail")

# IMPORTANT:
# - Conditions are checked TOP TO BOTTOM
# - First matching block executes
# - Remaining blocks are skipped

# ================================================
# 5.4 NESTED IF
# ================================================

age = 25
has_id = True

if age >= 18:
    if has_id:
        print("Allowed entry")
    else:
        print("ID required")
else:
    print("Underage")

# ================================================
# 5.5 SHORT-HAND IF (TERNARY OPERATOR)
# ================================================

age = 20

status = "Adult" if age >= 18 else "Minor"
print(status)

# ================================================
# 5.6 TRUTHY & FALSY VALUES (VERY IMPORTANT)
# ================================================

# Falsy values in Python:
# False, None, 0, 0.0, "", [], {}, set()

if []:
    print("This will NOT execute")
else:
    print("Empty list is falsy")

# ================================================
# 5.7 FOR LOOP
# ================================================

# for loop is used to iterate over sequences

nums = [10, 20, 30]

for num in nums:
    print(num)

# ================================================
# 5.8 range() FUNCTION WITH FOR LOOP
# ================================================

# range(start, stop, step)

for i in range(1, 6):
    print(i)

for i in range(0, 10, 2):
    print(i)

# ================================================
# 5.9 LOOPING WITH INDEX (enumerate)
# ================================================

fruits = ["apple", "banana", "cherry"]

for index, fruit in enumerate(fruits):
    print(index, fruit)

# ================================================
# 5.10 LOOPING OVER DICTIONARY
# ================================================

student = {"name": "Jay", "age": 29}

for key in student:
    print(key)

for value in student.values():
    print(value)

for key, value in student.items():
    print(key, value)

# ================================================
# 5.11 WHILE LOOP
# ================================================

count = 0

while count < 3:
    print(count)
    count += 1

# ================================================
# 5.12 break STATEMENT
# ================================================

# break exits the loop immediately

for i in range(10):
    if i == 5:
        break
    print(i)

# ================================================
# 5.13 continue STATEMENT
# ================================================

# continue skips current iteration

for i in range(5):
    if i == 2:
        continue
    print(i)

# ================================================
# 5.14 pass STATEMENT
# ================================================

# pass is a placeholder (does nothing)

for i in range(3):
    if i == 1:
        pass
    else:
        print(i)


# Deep dive more into pass, break and continue:

# Pass: The pass statement in Python is used when a statement or a condition is required to be present in the program, but we don’t want any command or code to execute. It’s typically used as a "placeholder" for future code.
# Continue: The continue statement in Python is used to skip the remaining code inside a loop for the current iteration only
# Break: A break statement in Python alters the flow of a loop by terminating it once a specified condition is met.

# Break statement example below:

for k in range(0,5):
    print(f'Outer For Loop Iteration: {k}')
    for num in range(0,10):
        if num == 5:
            break
        print(f'--Inner For Loop Iteration: {num}')


# output of above code:

# Outer For Loop Iteration: 0
# --Inner For Loop Iteration: 0
# --Inner For Loop Iteration: 1
# --Inner For Loop Iteration: 2
# --Inner For Loop Iteration: 3
# --Inner For Loop Iteration: 4
# Outer For Loop Iteration: 1
# --Inner For Loop Iteration: 0
# --Inner For Loop Iteration: 1
# --Inner For Loop Iteration: 2
# --Inner For Loop Iteration: 3
# --Inner For Loop Iteration: 4
# Outer For Loop Iteration: 2
# --Inner For Loop Iteration: 0
# --Inner For Loop Iteration: 1
# --Inner For Loop Iteration: 2
# --Inner For Loop Iteration: 3
# --Inner For Loop Iteration: 4
# Outer For Loop Iteration: 3
# --Inner For Loop Iteration: 0
# --Inner For Loop Iteration: 1
# --Inner For Loop Iteration: 2
# --Inner For Loop Iteration: 3
# --Inner For Loop Iteration: 4
# Outer For Loop Iteration: 4
# --Inner For Loop Iteration: 0
# --Inner For Loop Iteration: 1
# --Inner For Loop Iteration: 2
# --Inner For Loop Iteration: 3
# --Inner For Loop Iteration: 4

# explaination of above code output:

# As we can see in the above picture, for every iteration of the outer for loop, the flow of the inner loop breaks after five iterations, as per the condition num == 5.

# Thus, if the break statement is inside a nested loop (a loop inside another loop), the break statement will terminate the innermost loop.


# Pass example:

for num in range(0,10):
    if num == 5:
        pass
    print(f'Iteration: {num}')

# output of above code:

# Iteration: 0
# Iteration: 1
# Iteration: 2
# Iteration: 3
# Iteration: 4
# Iteration: 5
# Iteration: 6
# Iteration: 7
# Iteration: 8
# Iteration: 9

# explaination of above code:

# As we see in the above output, the pass statement really did nothing as the for loop and all statements within it are executed. 

# The pass statement is typically used while creating a method that we don’t want to use right now. It’s often used as a placeholder for future code.

# Most of the time, a pass statement is replaced with another meaningful command or code in a program.



# Continue Statement in Python:

# The continue statement is used to skip the remaining code inside a loop for the current iteration only.

for num in range(0,10):
    if num == 5:
        continue
    print(f'Iteration: {num}')

# output of above code:

# Iteration: 0
# Iteration: 1
# Iteration: 2
# Iteration: 3
# Iteration: 4
# Iteration: 6
# Iteration: 7
# Iteration: 8
# Iteration: 9

# explaination of above output:

# When the condition num == 5 becomes True, the continue statement gets executed. The remaining code in the loop is skipped only for that iteration. That’s why Iteration: 5 is missing from the above output.

# Therefore, the continue statement works opposite to the break statement. Instead of terminating the loop, it forces it to execute the next iteration of the loop.

# Continue statement 2 loop example:

for k in range(0,5):
    print(f'Outer For Loop Iteration: {k}')
    for num in range(0,10):
        if num == 5:
            continue
        print(f'--Inner For Loop Iteration: {num}')

# output of above code:

# Outer For Loop Iteration: 1
# --Inner For Loop Iteration: 0
# --Inner For Loop Iteration: 1
# --Inner For Loop Iteration: 2
# --Inner For Loop Iteration: 3
# --Inner For Loop Iteration: 4
# --Inner For Loop Iteration: 6
# --Inner For Loop Iteration: 7
# --Inner For Loop Iteration: 8
# --Inner For Loop Iteration: 9
# Outer For Loop Iteration: 2
# --Inner For Loop Iteration: 0
# --Inner For Loop Iteration: 1
# --Inner For Loop Iteration: 2
# --Inner For Loop Iteration: 3
# --Inner For Loop Iteration: 4
# --Inner For Loop Iteration: 6
# --Inner For Loop Iteration: 7
# --Inner For Loop Iteration: 8
# --Inner For Loop Iteration: 9
# Outer For Loop Iteration: 3
# --Inner For Loop Iteration: 0
# --Inner For Loop Iteration: 1
# --Inner For Loop Iteration: 2
# --Inner For Loop Iteration: 3
# --Inner For Loop Iteration: 4
# --Inner For Loop Iteration: 6
# --Inner For Loop Iteration: 7
# --Inner For Loop Iteration: 8
# --Inner For Loop Iteration: 9
# Outer For Loop Iteration: 4
# --Inner For Loop Iteration: 0
# --Inner For Loop Iteration: 1
# --Inner For Loop Iteration: 2
# --Inner For Loop Iteration: 3
# --Inner For Loop Iteration: 4
# --Inner For Loop Iteration: 6
# --Inner For Loop Iteration: 7
# --Inner For Loop Iteration: 8
# --Inner For Loop Iteration: 9
# ================================================
# 5.15 LOOP ELSE (LESS KNOWN BUT IMPORTANT)
# ================================================

# else executes ONLY if loop completes normally
# (i.e., no break occurred)

for i in range(5):
    if i == 10:
        break
else:
    print("Loop completed without break")

# ================================================
# 5.16 MATCH – CASE (Python 3.10+)
# ================================================

# Similar to switch-case in other languages

day = 3

match day:
    case 1:
        print("Monday")
    case 2:
        print("Tuesday")
    case 3:
        print("Wednesday")
    case _:
        print("Invalid day")

# ================================================
# 5.17 REAL-WORLD EXAMPLE
# ================================================

# Example: Login check

username = "admin"
password = "1234"

if username == "admin" and password == "1234":
    print("Login successful")
else:
    print("Invalid credentials")

# ================================================
# SUMMARY
# ================================================

# ✔ if / elif / else control decision making
# ✔ for loop is used for sequences
# ✔ while loop runs based on condition
# ✔ break exits loop
# ✔ continue skips iteration
# ✔ pass acts as placeholder
# ✔ match-case handles multi-branch logic
# ✔ Python evaluates conditions top to bottom

# ================================================
# END OF CONTROL STATEMENTS
# ================================================
