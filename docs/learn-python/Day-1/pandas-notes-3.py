import pandas as pd
import numpy as np

# Creating a "Messy" DataFrame
data = {
    'Product': ['Apple', 'Banana', 'Orange', 'Apple', 'Banana', 'Grape'],
    'Price':   [100,     50,       np.nan,   100,     50,       np.nan],  # Missing Prices
    'Stock':   [500,     200,      100,      500,     20,       300],
    'City':    ['NY',    'LA',     'NY',     'NY',    'LA',     'DC']
}

df = pd.DataFrame(data)

print("--- Original Messy Data ---")
print(df)

# ========================================
# 2.1 Inspection (Knowing what you have)
# ========================================

# Before you touch data, you must understand it. There are 2 "Magic Commands" for this.

# A. df.info() - The Meta-Data Check Tells you data types and missing values.

# Look for "Non-Null Count". 
# If 'Price' says 4 non-null but total entries are 6, you know you have 2 missing values.

print(df.info())

# B. df.describe() - The Statistical Check Gives you math stats (Mean, Min, Max) for numerical columns only.

# Useful to check for weird outliers (e.g., if 'Price' min is -500, something is wrong).

print(df.describe())

# ========================================
# 2.2 Selection: .loc vs .iloc (Crucial)
# ========================================

# This is where most beginners get stuck.

# .loc = Selection by Label (Name).

# .iloc = Selection by Integer Position (0, 1, 2...).

# Let's set a custom index to see the difference clearly.

df_indexed = df.set_index('Product') # we did this thig just to understand how this 'loc' works...
# Now the 'Rows' are named Apple, Banana, etc. this is like we gave the row names insted of normal index 0, 1,2... we changed this number to product name

print(df_indexed)

# output of above statement

#          Price  Stock City
# Product
# Apple    100.0    500   NY
# Banana    50.0    200   LA
# Orange     NaN    100   NY
# Apple    100.0    500   NY
# Banana    50.0     20   LA
# Grape      NaN    300   DC

# 1. .loc (Use the NAME)

# "Give me the row named 'Orange'"
print(df_indexed.loc['Orange'])

# 2. .iloc (Use the POSITION)
# "Give me the 2nd row (Index 1)"
print(df_indexed.iloc[1])
# "Give me the !st and 2nd row (Index 0 and 1)"
print(df_indexed.iloc[0:2])

# output of above one:

#          Price  Stock City
# Product
# Apple    100.0    500   NY
# Banana    50.0    200   LA

# select 1 column from dataframe:

new_df = df['City']

# select 2 columns(or multiple) from dataframe:

new_df = df[['City','Stock']]


# ========================================
# 2.3 Filtering (The "SQL WHERE" Clause)
# ========================================

# You don't loop through rows to find things. You use Boolean Masking.

# Syntax: df[ condition ]

# 1. Simple Filter
# "Show me rows where Price > 60"
expensive = df[df['Price'] > 60]
print(expensive)

# 2. Multiple Conditions
# (AND = &)  (OR = |)
# CRITICAL: You MUST wrap each condition in parentheses ( )
# "City is NY AND Stock is over 300"
ny_high_stock = df[ (df['City'] == 'NY') & (df['Stock'] > 300) ]
print(ny_high_stock)

# ========================================
# 2.4 Cleaning (The "Fix" Phase)
# ========================================

# Now, let's fix the NaN and Duplicates we saw earlier.

# A. Handling Missing Data (NaN) You have two choices: Delete or Fill.

# Option 1: DESTROY rows with bad data
# If any column has NaN, the whole row is deleted.

clean_dropped = df.dropna()
print(clean_dropped) 
# Result: Orange and Grape are gone.


# Option 2: REPAIR data (Fill with 0)
# Replace NaN with 0 (or mean, or median)
clean_filled = df.fillna(0)
print(clean_filled)
# Result: Orange Price becomes 0.0.

# B. Removing Duplicates

# drop_duplicates() keeps the first one it sees, deletes the rest.
unique_df = df.drop_duplicates()
print(unique_df)
# Result: The second 'Apple' (Row 3) is removed.

# -----------------------------------------------------------------------------------------------------------------------------------------

# uderstanding cleaning in deeper way:

# ================================================
# 0. SETUP: CREATING THE "DIRTY" DATA
# ================================================
data = {
    'Product': ['Apple', 'Banana', 'Orange', 'Apple', 'Banana', 'Grape', 'Mango', 'Peach', 'Melon', 'Berry'],
    'Price':   [100,    np.nan,   80,       100,      50,       np.nan,  120,     90,      np.nan,   60],
    'Stock':   [500,    200,      100,      np.nan,   20,       300,     400,     np.nan,  150,      200],
    'Region':  ['US',   '-',      'UK',     'US',     '',       'US',    'UK',    '-',     'US',     'UK'], # '-' and empty strings
    'Date':    ['2023-01-01', '01/02/2023', '2023.01.03', 'Jan 4, 2023', '2023-01-05', 
                '06/01/2023', '2023-01-07', '2023-01-08', '2023-01-09', 'invalid_date'] # Mixed formats
}

df = pd.DataFrame(data)

print("--- 0. ORIGINAL DIRTY DATA ---")
print(df)
# Notice: 
# Price/Stock have NaN.
# Region has '-' and empty strings.
# Date has mixed formats (dashes, slashes, text).


# ================================================
# 1. FILLING NUMERIC MISSING VALUES (fillna)
# ================================================
# Q1: Does fillna(0) fill ALL columns?
# Answer: Yes, if you run df.fillna(0), it hits EVERYTHING (including Strings!). 
# Usually, you want to target specific columns.

# Bad Idea: df.fillna(0) -> Replaces Price NaNs, but might mess up other logic.

# Good Idea: Target specific column
# Let's fill 'Stock' with 0 (Assuming NaN means out of stock)
df['Stock'] = df['Stock'].fillna(0)

print("\n--- 1. AFTER FILLING STOCK WITH 0 ---")
print(df[['Product', 'Stock']])


# ================================================
# 2. FILLING WITH MEAN / MEDIAN
# ================================================
# Q2: How to fill with mean?
# Logic: You calculate the mean of the column *first*, then pass that number to fillna.

# Step A: Calculate the mean of Price (ignoring NaNs automatically)
avg_price = df['Price'].mean()
print(f"\n[Calculated Average Price: {avg_price}]")

# Step B: Fill only the Price column with that number
df['Price'] = df['Price'].fillna(avg_price)

print("--- 2. AFTER FILLING PRICE WITH MEAN ---")
print(df[['Product', 'Price']])


# ================================================
# 3. CLEANING STRING COLUMNS ('-' and Empty)
# ================================================
# Q3: Handling '-' or empty strings.
# Pandas DOES NOT see '-' as "missing". It sees it as the character dash.
# You must first replace them with np.nan (standard missing marker).

# Step A: Replace '-' and '' (empty) with NaN
df['Region'] = df['Region'].replace(['-', ''], np.nan)

# Step B: Now you can fill them. Let's say 'Unknown'
df['Region'] = df['Region'].fillna('Unknown')

print("\n--- 3. AFTER CLEANING REGION STRINGS ---")
print(df['Region'])


# ================================================
# 4. CLEANING DATES (The "Uniform" Fix)
# ================================================
# Q4: Different formats ('2023-01-01', 'Jan 4, 2023')
# Solution: pd.to_datetime() is a magical function. 
# It tries to guess the format automatically.

# 'errors=coerce' means: "If you can't read the date, turn it into NaT (Not a Time)"
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

print("\n--- 4. AFTER STANDARDIZING DATES ---")
print(df['Date'])
# Notice standard YYYY-MM-DD format.
# The 'invalid_date' became NaT (Missing).


print("\n--- FINAL CLEAN DATAFRAME ---")
print(df)

# Explanation of the Output

# Original Data: You see NaN in Price/Stock, '-' in Region, and weird dates.

# Stock (fillna 0): The NaNs in Stock became 0.0.

# Price (Mean): The NaNs in Price became 85.71 (the average of the existing prices). It did not use the Stock numbers, only the Price numbers.

# Region (Strings): The '-' and '' were successfully converted to 'Unknown'. If we hadn't replaced them with np.nan first, fillna would have ignored them!

# Dates: pd.to_datetime converted everything (even "Jan 4, 2023") into the standard ISO format 2023-01-04.

# -----------------------------------------------------------------------------------------------------------------------------------------------------

# Here are the Top 4 Other Cleaning Techniques you will use constantly:
# 1. Renaming Columns: Changing Sales (2023) to sales_2023 so it's easier to code.'
# 2. 'String Cleanup (.str): Trimming extra spaces (" Apple " $\rightarrow$ "Apple") or removing symbols ("$100" $\rightarrow$ 100).'
# 3. 'Type Conversion (astype): Converting "100" (String) to 100 (Integer).'
# 4. 'Dropping Columns: Deleting junk columns you don't need.Here is a script that combines all of these into a "Master Clean" workflow.


# ================================================
# 0. SETUP: EXTREMELY DIRTY DATA
# ================================================
data = {
    '  Product Name  ': ['  Laptop ', 'Mouse  ', ' Monitor', 'Laptop'], # Bad names & Spaces
    'Cost ($)':        ['$1,000', '$25', '$300', 'Not Sold'],           # Symbols & Text in number column
    'Is_In_Stock':     ['Yes', 'No', 'Yes', 'Yes'],
    'Unnecessary_ID':  [111, 222, 333, 444]                              # Junk column
}

df = pd.DataFrame(data)

print("--- 0. ORIGINAL DIRTY DATA ---")
print(df)
print("\n[Check Types]:")
print(df.dtypes) 
# Notice 'Cost ($)' is an Object (String), not a Number!


# ================================================
# 1. RENAMING COLUMNS (The 'rename' method)
# ================================================
# Problem: Columns have spaces and symbols. Hard to type df['  Product Name  '].
# Fix: Rename them to simple, lowercase words.

df = df.rename(columns={
    '  Product Name  ': 'product',
    'Cost ($)': 'price',
    'Is_In_Stock': 'stock'
})

print("\n--- 1. AFTER RENAMING COLUMNS ---")
print(df.columns)


# ================================================
# 2. DROPPING COLUMNS (The 'drop' method)
# ================================================
# Problem: We don't need 'Unnecessary_ID'.
# Fix: Drop it. axis=1 means "Column".

df = df.drop(columns=['Unnecessary_ID'])
# Alternative syntax: df.drop('Unnecessary_ID', axis=1)

print("\n--- 2. AFTER DROPPING JUNK ---")
print(df)


# ================================================
# 3. STRING CLEANUP (The '.str' Accessor)
# ================================================
# Problem: 'product' has spaces ("  Laptop ").
# Fix: Use .str.strip() (Just like Python's .strip())

df['product'] = df['product'].str.strip()

# Problem: 'price' has '$' and ',' and text "Not Sold".
# Fix: 
# A. Replace 'Not Sold' with NaN
# B. Replace '$' and ',' with empty string ''

df['price'] = df['price'].replace('Not Sold', np.nan)
df['price'] = df['price'].str.replace('$', '', regex=False)
df['price'] = df['price'].str.replace(',', '', regex=False)

print("\n--- 3. AFTER STRING CLEANUP ---")
print(df)
# Note: 'price' looks like numbers now, BUT it is still a String internally!


# ================================================
# 4. TYPE CONVERSION (The 'astype' method)
# ================================================
# Problem: Pandas still thinks 'price' is text because it started that way.
# Fix: Force it to be a Float.

df['price'] = df['price'].astype(float)

print("\n--- 4. AFTER TYPE CONVERSION ---")
print(df)
print(df.dtypes) 
# Now 'price' is float64. We can finally do math on it!

# Bonus: Calculate average price now that it's a number
print(f"\nAverage Price: {df['price'].mean()}")