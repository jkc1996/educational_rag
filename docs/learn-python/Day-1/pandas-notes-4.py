# Here is Section 3: Analysis (Grouping, Merging & Exporting).

# This is the most powerful part of Pandas. 
# 
# This is where you stop just "fixing" data and start answering questions like "Which city sells the most?" or "Who is our best customer?".

# It covers 3 main concepts:

# Grouping (groupby): The "Pivot Table" feature.

# Merging (merge): The "VLOOKUP" or "SQL JOIN" feature.

# Exporting (to_csv): Saving your work.

import pandas as pd
import numpy as np

# ================================================
# 0. SETUP: CREATING DATA FOR ANALYSIS
# ================================================
# We need two related tables to demonstrate Merging.
# 1. Sales Table: Transactions
# 2. Managers Table: Who manages which Region

sales_data = {
    'OrderID': [101, 102, 103, 104, 105, 106],
    'Region':  ['North', 'South', 'North', 'East', 'North', 'South'],
    'Product': ['Laptop', 'Mouse', 'Laptop', 'Monitor', 'Mouse', 'Monitor'],
    'Sales':   [1000, 20, 1000, 300, 25, 300]
}

managers_data = {
    'Region':  ['North', 'South', 'East', 'West'],
    'Manager': ['Alice', 'Bob', 'Charlie', 'David']
}

df_sales = pd.DataFrame(sales_data)
df_managers = pd.DataFrame(managers_data)

print("--- 1. SALES TABLE ---")
print(df_sales)
print("\n--- 2. MANAGERS TABLE ---")
print(df_managers)


# ================================================
# 1. GROUPBY (The "Pivot Table")
# ================================================
# Used to Aggregate data.
# Syntax: df.groupby('Column_To_Group_By')['Column_To_Math'].function()

print("\n--- 3. GROUPBY EXAMPLES ---")

# Example A: "What are the Total Sales per Region?"
region_sales = df_sales.groupby('Region')['Sales'].sum()
print("Total Sales per Region:\n", region_sales)
# Output:
# East      300
# North    2025
# South     320

# Example B: "What is the Average Sales Price per Product?"
product_avg = df_sales.groupby('Product')['Sales'].mean()
print("\nAvg Price per Product:\n", product_avg)
# Output:
# Laptop     1000.0
# Monitor     300.0
# Mouse        22.5

# Example C: Multiple Aggregations (Count, Min, Max, Mean)
# "Give me stats on Sales for each Region"
summary = df_sales.groupby('Region')['Sales'].agg(['count', 'sum', 'mean'])
print("\nDetailed Summary:\n", summary)


# ================================================
# 2. VALUE_COUNTS (Frequency Check)
# ================================================
# The fastest way to see "How many times does X appear?"

print("\n--- 4. VALUE COUNTS ---")
# "Which region has the most orders?"
print(df_sales['Region'].value_counts())
# Output:
# North    3
# South    2
# East     1


# ================================================
# 3. SORTING (Ordering Data)
# ================================================
# sort_values(by='Column', ascending=True/False)

print("\n--- 5. SORTING ---")
# Show highest sales first
sorted_df = df_sales.sort_values(by='Sales', ascending=False)
print(sorted_df)


# ================================================
# 4. MERGING (SQL Join / VLOOKUP)
# ================================================
# We have Sales data, but we don't know the Manager's name.
# The 'Region' column exists in BOTH tables. We join on that.

# Syntax: pd.merge(left_table, right_table, on='Key_Column', how='inner/left')

print("\n--- 6. MERGING TABLES ---")

# Inner Join: Only keep rows where Region exists in BOTH
merged_df = pd.merge(df_sales, df_managers, on='Region', how='left')

print(merged_df)
# Output:
#    OrderID Region  Product  Sales  Manager
# 0      101  North   Laptop   1000    Alice
# 1      102  South    Mouse     20      Bob
# ...
# (Notice "Manager" is now added to the sales data!)


# ================================================
# 5. EXPORTING (Saving Results)
# ================================================
# Once you have your final clean, merged dataframe, you save it.

# index=False means "Don't save the 0,1,2 row numbers"
merged_df.to_csv('final_report.csv', index=False)
print("\n--- 7. EXPORT COMPLETE ---")
print("Saved 'final_report.csv' to disk.")


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------

# some more things on aggregation

# ================================================
# 0. SETUP: EMPLOYEE DATA
# ================================================
data = {
    'Department': ['IT', 'IT', 'IT', 'HR', 'HR', 'Sales', 'Sales', 'Sales'],
    'Employee':   ['Alice', 'Bob', 'Charlie', 'David', 'Eva', 'Frank', 'Grace', 'Hank'],
    'Salary':     [120000, 80000, 95000, 60000, 65000, 50000, 200000, np.nan], # Hank has missing salary
    'Years_Exp':  [5, 2, 3, 4, 5, 1, 10, 2]
}

df = pd.DataFrame(data)

print("--- ORIGINAL DATA ---")
print(df)
print("\n" + "="*40 + "\n")


# We group by 'Department' for all examples
grouped = df.groupby('Department')['Salary']


# ================================================
# 1. MATH FUNCTIONS (Aggregates values)
# ================================================

print("--- 1. MATH EXAMPLES ---")

# .sum() - Total Salary bill per Dept
# Note: Hank's NaN is treated as 0 for sum
print("Sum:\n", grouped.sum()) 

# .mean() - Average Salary
# Note: Skips NaN values automatically
print("\nMean (Average):\n", grouped.mean())

# .median() - The Middle Value (Good for ignoring outliers like Grace's 200k)
print("\nMedian (Middle):\n", grouped.median())

# .std() - Standard Deviation (How much salaries vary)
# Sales will be huge because of the gap between 50k and 200k
print("\nStd Dev (Variation):\n", grouped.std())

# .min() and .max() - Lowest and Highest earner
print("\nMin (Lowest):\n", grouped.min())
print("\nMax (Highest):\n", grouped.max())


# ================================================
# 2. COUNTING (Count vs Size)
# ================================================

print("\n" + "="*40 + "\n")
print("--- 2. COUNTING EXAMPLES ---")

# .count() - Counts NON-NULL values
# Notice Sales is 2 (because Hank has NaN salary)
print("Count (Valid Values):\n", grouped.count())

# .size() - Counts TOTAL ROWS (including missing data)
# Notice Sales is 3 (Alice, Grace, Hank)
print("\nSize (Total Rows):\n", grouped.size())


# ================================================
# 3. SELECTION (First vs Last)
# ================================================
# Useful to grab a representative example from each group.

print("\n" + "="*40 + "\n")
print("--- 3. SELECTION EXAMPLES ---")

# .first() - Returns the first row appearing in that group
print("First entry per group:\n", grouped.first())

# .last() - Returns the last row appearing in that group
print("\nLast entry per group:\n", grouped.last())

# BONUS: .nth() - Get the Nth row (e.g., the 2nd person in every dept)
print("\n2nd entry (nth(1)):\n", grouped.nth(1))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# 1. apply() and lambda (Custom Functions)

# Sometimes the built-in functions (.sum(), .mean()) aren't enough. You need to do something weird to every row.

# Scenario: "If the price is > 100, label it 'High', otherwise 'Low'."

import pandas as pd

df = pd.DataFrame({'Price': [50, 150, 80, 200]})

# syntax: df['col'].apply(lambda x: result)
df['Label'] = df['Price'].apply(lambda x: 'High' if x > 100 else 'Low')

print(df)
# Output:
#    Price Label
# 0     50   Low
# 1    150  High
# 2     80   Low
# 3    200  High



# 2. Pivot Tables (pivot_table)

# You know groupby. pivot_table is its fancier cousin. It looks exactly like Excel Pivot Tables. It allows you to group by Rows AND Columns at the same time.

# Scenario: "Show me average sales, broken down by Region (Rows) and Product (Columns)."

data = {
    'Region': ['North', 'North', 'South', 'South'],
    'Product': ['Laptop', 'Mouse', 'Laptop', 'Mouse'],
    'Sales': [1000, 50, 800, 40]
}
df = pd.DataFrame(data)

pivot = df.pivot_table(index='Region', columns='Product', values='Sales', aggfunc='sum')

print(pivot)
# Output:
# Product  Laptop  Mouse
# Region
# North      1000     50
# South       800     40