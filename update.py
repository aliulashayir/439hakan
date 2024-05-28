import hashlib
import getpass
import json
import logging
#ADMIN PASSWORD hakan123
def load_key_from_file(filename):
    try:
        with open(filename, 'r') as file:
            key_data = file.read().strip()
        return key_data
    except FileNotFoundError:
        return None

def save_key_to_file(key, filename):
    with open(filename, 'w') as file:
        file.write(key)

def hash_password(password): #ADMIN PASSWORD hakan123
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_admin():
    stored_password_hash = load_key_from_file('db/admin_password.txt')

    attempts = 3
    while attempts > 0:
        password = getpass.getpass("Enter admin password: ")
        if hash_password(password) == stored_password_hash:
            return True
        else:
            print("Authentication failed. Please try again.")
            attempts -= 1

    print("Too many failed attempts. Exiting.")
    return False
    
def update_auth_server_key():
    admin_authenticated = authenticate_admin()
    if not admin_authenticated:
        return

    new_server_key = input("Enter the new Auth server key: ")
    hashed_server_key = hashlib.sha256(new_server_key.encode()).hexdigest()

    save_key_to_file(hashed_server_key, 'db/auth_server_key.txt')

    print("Auth server key updated successfully.")

def update_admin_password():
    admin_authenticated = authenticate_admin()
    if not admin_authenticated:
        return

    new_admin_password = getpass.getpass("Enter the new admin password: ")
    hashed_admin_password = hash_password(new_admin_password)

    save_key_to_file(hashed_admin_password, 'db/admin_password.txt')

    print("Admin password updated successfully.")

if __name__ == "__main__":
    print("Key Management Script")
    print("1. Update Auth Server Key")
    print("2. Update Admin Password")
    choice = input("Enter your choice (1/2): ")

    if choice == '1':
        update_auth_server_key()
    elif choice == '2':
        update_admin_password()
    else:
        print("Invalid choice.")
