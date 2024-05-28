import hashlib
import json

# Hash function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create user credentials dictionary with hashed passwords
user_credentials = {
    'user1': {'password_hash': hash_password('password123')},
    'user2': {'password_hash': hash_password('securepass')}
}

# Save user credentials to a JSON file
with open('user_credentials.json', 'w') as json_file:
    json.dump(user_credentials, json_file)
