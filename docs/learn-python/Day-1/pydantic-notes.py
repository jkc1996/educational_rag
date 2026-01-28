# ================================================
# PYDANTIC BASICS: DATA VALIDATION
# ================================================

# Pydantic enforces data types using Python "Type Hints".
# It parses (fixes) data when possible, and errors when impossible.

# Install: pip install pydantic

from pydantic import BaseModel, ValidationError
from typing import List, Optional

# ------------------------------------------------
# 1. THE BASEMODEL (The Core)
# ------------------------------------------------
# Define your data structure as a class inheriting from BaseModel.

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True  # Default value is True if not provided

print("--- 1. Valid Creation ---")
# Perfect data matches the types exactly
user = User(id=1, username="jdoe", email="j@doe.com")
print(user)
# Output: id=1 username='jdoe' email='j@doe.com' is_active=True


# ------------------------------------------------
# 2. TYPE COERCION (The "Auto-Fix")
# ------------------------------------------------
# Pydantic is smart. If you send a String "123" to an Int field,
# it converts it automatically.

print("\n--- 2. Type Coercion ---")
# 'id' is sent as string "500", 'is_active' as string "False"
user_mixed = User(id="500", username="alice", email="a@a.com", is_active="False")

print(f"ID Type: {type(user_mixed.id)}") 
# Output: <class 'int'> (It converted "500" -> 500)
print(f"Active: {user_mixed.is_active}") 
# Output: False (It converted "False" -> False)


# ------------------------------------------------
# 3. ERROR HANDLING (ValidationError)
# ------------------------------------------------
# When data cannot be fixed (e.g., "apple" is not an integer), it crashes safely.

print("\n--- 3. Validation Errors ---")
try:
    # Sending 'apple' to an int field
    User(id="apple", username="bob", email="b@b.com")
except ValidationError as e:
    print("Error Found:")
    print(e)
    # Output: 
    # 1 validation error for User
    # id
    #   Input should be a valid integer ...


# ------------------------------------------------
# 4. COMPLEX TYPES (List & Optional)
# ------------------------------------------------
# Real data is nested.

class Product(BaseModel):
    name: str
    tags: List[str]            # Must be a list of strings
    description: Optional[str] = None # Can be a string OR None (null)

print("\n--- 4. Complex Types ---")
# Valid product with tags
p1 = Product(name="Laptop", tags=["tech", "sale"])
print(p1.tags)

# Product with NO description (defaults to None)
p2 = Product(name="Mouse", tags=[])
print(p2)


# ------------------------------------------------
# 5. EXPORTING DATA (Model -> Dict/JSON)
# ------------------------------------------------
# You usually need to turn the Object back into a Dictionary/JSON for APIs.

print("\n--- 5. Exporting ---")
p = Product(name="Phone", tags=["5g"], description="New Model")

# Method A: To Dictionary (Python dict)
# Note: In Pydantic V2, use .model_dump(). (Old V1 used .dict())
data_dict = p.model_dump()
print(f"As Dict: {data_dict}")
print(f"Type: {type(data_dict)}")

# Method B: To JSON String (For sending over API)
# Note: In Pydantic V2, use .model_dump_json(). (Old V1 used .json())
data_json = p.model_dump_json()
print(f"As JSON: {data_json}")
print(f"Type: {type(data_json)}")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# ================================================
# ADVANCED PYDANTIC (VALIDATORS & NESTING)
# ================================================

from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError
from typing import List, Optional

# ------------------------------------------------
# 1. FIELD CONSTRAINTS (The "Field" object)
# ------------------------------------------------
# Used for simple rules like "Age > 0" or "Name < 10 chars"
# You don't need to write a function for these.

class Item(BaseModel):
    # gt=0 -> Greater Than 0
    # le=1000 -> Less than or Equal to 1000
    price: float = Field(gt=0, le=1000, description="Price must be positive")
    
    # min_length=3 -> String must be at least 3 chars
    name: str = Field(min_length=3, max_length=50)

print("--- 1. Field Constraints ---")
try:
    Item(name="TV", price=-50) # Fail: Name too short, Price negative
except ValidationError as e:
    print(e)
    # Output: 
    # 1. Price should be greater than 0
    # 2. String should have at least 3 characters


# ------------------------------------------------
# 2. CUSTOM VALIDATORS (@field_validator)
# ------------------------------------------------
# Use this when you need Python logic (Regex, API checks, cleaning data).
# Rule: If valid, RETURN the value. If invalid, RAISE ValueError.

class User(BaseModel):
    username: str
    role: str

    @field_validator('role')
    @classmethod
    def check_role(cls, v):
        # 'v' is the value being validated
        allowed = ['admin', 'user', 'guest']
        if v.lower() not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v.lower() # We can also modify/clean the data here!

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.upper() # Converting to Uppercase automatically

print("\n--- 2. Custom Validators ---")
try:
    u = User(username="john_doe", role="SUPERUSER")
except ValidationError as e:
    print(e)
    # Output: 
    # 1. Username must be alphanumeric (failed because of '_')
    # 2. Role must be one of ['admin', 'user', 'guest']

# Valid Example (Notice it auto-fixes case)
u_valid = User(username="john123", role="ADMIN")
print(f"Cleaned Data: {u_valid}") 
# Output: username='JOHN123' role='admin'


# ------------------------------------------------
# 3. MODEL VALIDATORS (Multi-Field Logic)
# ------------------------------------------------
# Use this to compare two fields (e.g., Start Date vs End Date).

class ChangePassword(BaseModel):
    password: str
    confirm_password: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        # 'self' gives access to the whole model
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

print("\n--- 3. Model Validators ---")
try:
    ChangePassword(password="secret123", confirm_password="wrong")
except ValidationError as e:
    print("Error: Passwords do not match")


# ------------------------------------------------
# 4. NESTED MODELS (Composition)
# ------------------------------------------------
# Essential for complex JSON APIs.

class Address(BaseModel):
    city: str
    zipcode: str

class Customer(BaseModel):
    name: str
    # nesting the Address model inside Customer
    address: Address 
    previous_addresses: List[Address] = []

print("\n--- 4. Nested Models ---")
# Incoming complex JSON data
incoming_data = {
    "name": "Alice",
    "address": {
        "city": "New York",
        "zipcode": "10001"
    },
    "previous_addresses": [
        {"city": "Boston", "zipcode": "02108"}
    ]
}

c = Customer(**incoming_data) # ** unpacks the dictionary
print(f"Customer City: {c.address.city}")
print(f"Previous City: {c.previous_addresses[0].city}")