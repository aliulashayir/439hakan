import socket
import threading
import hashlib
import json
from datetime import datetime, timedelta
import ssl
import logging

"""
    user_credentials = {
    'user1': {'password_hash': hashlib.sha256('password123'.encode()).hexdigest()},
    'user2': {'password_hash': hashlib.sha256('securepass'.encode()).hexdigest()}
    }
"""

# Set up logging
logging.basicConfig(filename='log/auth_server_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Load user credentials from a file (replace this with your file path)
with open('user_credentials.json', 'r') as user_file:
    user_credentials = json.load(user_file)

def hash_password(password):
    # Hash the password using a secure hash function
    return hashlib.sha256(password.encode()).hexdigest()

def generate_ticket(username, expiration_time): #TİCKET GRANTİNG TİCKET OLUŞTURULUP TGS YE GÖNDERİLİK
    # Generate a secure ticket containing user information
    ticket_data = {
        'username': username,
        'expiration_time': expiration_time.isoformat(),
    }
    return json.dumps(ticket_data).encode()

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024)
        if not data:
            return

        credentials = json.loads(data.decode())
        username = credentials.get('username', '')
        password = credentials.get('password', '')

        # Check if the provided username exists and the password is correct
        if username in user_credentials and hash_password(password) == user_credentials[username]['password_hash']:
            # Authentication successful

            # Generate and send a Ticket-Granting Ticket (TGT) to the client
            expiration_time = datetime.now() + timedelta(minutes=30)
            tgt = generate_ticket(username, expiration_time)
            client_socket.send(tgt)
            logging.info(f"Authentication successful for user: {username}")

        else:
            # Authentication failed
            client_socket.send(b'Invalid credentials')
            logging.warning(f"Authentication failed for user: {username}")

    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        client_socket.close()

def auth_server():
    # Set up the server socket
    server_host = '127.0.0.1'
    server_port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Create an SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='cert/auth_server.crt', keyfile='cert/auth_server.key')

    # Wrap the server socket with SSL/TLS
    server_socket = ssl_context.wrap_socket(server_socket, server_side=True)

    server_socket.bind((server_host, server_port))
    server_socket.listen(5)

    logging.info(f"[*] Authentication Server listening on {server_host}:{server_port}")

    try:
        while True:
            # Accept incoming connections
            client_socket, addr = server_socket.accept()
            logging.info(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

            # Start a new thread to handle the client
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        logging.info("\n[*] Authentication Server shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    auth_server()
