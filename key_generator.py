
import os
    
import hashlib
import getpass
import json


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Get admin password from the user
admin_password = getpass.getpass("Enter admin password: ")

# Hash the admin password
hashed_admin_password = hash_password(admin_password)

# Save hashed admin password to a file
with open('db/admin_password.txt', 'w') as file:
    file.write(hashed_admin_password)

print("Hashed admin password saved to admin_password.txt.")    
