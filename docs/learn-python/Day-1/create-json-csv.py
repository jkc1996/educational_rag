import pandas as pd
import json

# --- 1. Create the CSV File ---
csv_content = """Product,Price,Stock
Laptop,1000,50
Mouse,25,200
Monitor,300,75
"""

# Write to 'products.csv'
with open('products.csv', 'w') as f:
    f.write(csv_content)

print("Created products.csv!")

# --- 2. Create the JSON File ---
json_content = [
    {"Product": "Laptop", "Price": 1000, "Stock": 50},
    {"Product": "Mouse", "Price": 25, "Stock": 200},
    {"Product": "Monitor", "Price": 300, "Stock": 75}
]

# Write to 'products.json'
with open('products.json', 'w') as f:
    json.dump(json_content, f)

print("Created products.json!")