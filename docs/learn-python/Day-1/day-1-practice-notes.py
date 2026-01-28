# Online Python Playground
# Use the online IDE to write, edit & run your Python code
# Create, edit & delete files online

print("Try programiz.pro")

x = {5, 6, 7}
print(x) # {5, 6, 7}

x.add(8)
print(x) # {8, 5, 6, 7}
x.add(5) # ignore
print(x) # {8, 5, 6, 7}

student = {
    "name": "Jay",
    "age": 29
}

print(student) # {'name': 'Jay', 'age': 29}

student["std"] = 8

print(student) # {'name': 'Jay', 'age': 29, 'std': 8}

student["name"] = "vishal"

print(student) # {'name': 'Jay', 'age': 29, 'std': 8}

my_list = ["Banana", "apple", "Grape", "pear"]
my_list.sort(key=str.lower)
print(my_list)

a = [5, 6, 7, 8, 7]
print(a.index(5))

numbers = (1, 2, 3, 4, 5)

first,second, *middle, last = numbers

print(first)          # 1
print(middle)         # [3, 4]
print(last)           # 5

x = [4, 5, 6, 6, 7]
print(set(x))
print(tuple(x))

y = {3, 4, 6, 6, 7}
print(list(y))
print(tuple(y))

z = (3, 5, 7, 9, 9, 8)
print(list(z))
print(set(z))

for i in range(5): # this will skip 2 and print 0, 1, 3, 4 (skip 2 and contine with next iteration)
    if i == 2:
        continue
    print(i)

for i in range(5): # break the loop as soon as i = 3, o/p will be 0, 1, 2
  if i == 3:
    break
  print(i)

for i, value in enumerate(my_list):
  print(i, value)

for i in range(0, 10, 2): # print number 0 to 10 with step size 2.
    print(i)