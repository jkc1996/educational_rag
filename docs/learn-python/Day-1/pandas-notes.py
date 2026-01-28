import pandas as pd
import json
import os

# Learning path:

# Section - 1: The Foundation: Series, DataFrames, and Loading Data.

# Section - 2: The Inspection: Slicing, Dicing, and Cleaning.

# Section - 3: The Power: Grouping, Merging, and Analytics.

# ================================================
# 0. SETUP (GENERATING DUMMY DATA FOR LEARNING)
# ================================================
# We create these files dynamically so the 'Loading Data' section works for you.

# 1. Create a dummy CSV


# csv_content = """Product,Price,Stock
# Laptop,1000,50
# Mouse,25,200
# Monitor,300,75
# """
# with open('products_dummy.csv', 'w') as f:
#     f.write(csv_content)

# # 2. Create a dummy JSON
# json_content = [
#     {"Product": "Laptop", "Price": 1000, "Stock": 50},
#     {"Product": "Mouse", "Price": 25, "Stock": 200},
#     {"Product": "Monitor", "Price": 300, "Stock": 75}
# ]
# with open('products_dummy.json', 'w') as f:
#     json.dump(json_content, f)

# print("Setup Complete: 'products_dummy.csv' and 'products_dummy.json' created.\n")


# ================================================
# 1. PANDAS FOUNDATION (SERIES & DATAFRAMES)
# ================================================

# Pandas is the "Excel" of Python.
# It provides structured data types: Series (1D) and DataFrame (2D).

# ------------------------------------------------
# 1.1 The Series (1D Data)
# ------------------------------------------------
# Think of this as a single column in Excel.
# It has VALUES and an INDEX (Labels).

data = [10, 20, 30]
s = pd.Series(data)

print("--- Basic Series ---")
print(s)
# Output:
# 0    10
# 1    20
# 2    30
# dtype: int64

# Custom Indexing (The Power Move)
# You can give rows names instead of 0, 1, 2.
s_custom = pd.Series([100, 200, 300], index=['Apple', 'Banana', 'Cherry'])

print("\n--- Custom Index Series ---")
print(s_custom)
# Output:
# Apple     100
# Banana    200
# Cherry    300

# Accessing by Label
print(f"Price of Banana: {s_custom['Banana']}")  # 200

# ------------------------------------------------
# 1.2 The DataFrame (2D Data / Table)
# ------------------------------------------------
# A collection of Series that share the same Index.
# Usually created from a Dictionary of Lists.

data_dict = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'Paris', 'London']
}

df = pd.DataFrame(data_dict)

print("\n--- DataFrame Created from Dictionary ---")
print(df)
# Output:
#       Name  Age      City
# 0    Alice   25  New York
# 1      Bob   30     Paris
# 2  Charlie   35    London

# ------------------------------------------------
# 1.3 The Anatomy of a DataFrame
# ------------------------------------------------
# How to access the raw components.

print("\n--- Anatomy ---")
print("Columns:", df.columns)  # Index(['Name', 'Age', 'City'], dtype='object')
print("Index:  ", df.index)    # RangeIndex(start=0, stop=3, step=1)
print("Values: \n", df.values) # Raw NumPy array of data

# ------------------------------------------------
# 1.4 Loading Data (I/O)
# ------------------------------------------------
# In the real world, you read files, not dictionaries.

# Reading CSV
# header=0 implies the first row contains column names.
df_csv = pd.read_csv('products.csv')

print("\n--- Loaded from CSV ---")
print(df_csv)

# Reading JSON
df_json = pd.read_json('products.json')

print("\n--- Loaded from JSON ---")
print(df_json)

# ------------------------------------------------
# 1.5 Quick Inspection
# ------------------------------------------------
# When data is huge, use these to peek.

print("\n--- Head (First 5 rows) ---")
print(df_csv.head())

print("\n--- Shape (Rows, Cols) ---")
print(df_csv.shape)  # (3, 3)

# Clean up dummy files (Optional)
# os.remove('products_dummy.csv')
# os.remove('products_dummy.json')

# -------------------------------------------------------------------------------------------------------------------------------------------------------------

