import socket
import threading
import json
from datetime import datetime, timedelta
import ssl
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

# Set up logging
logging.basicConfig(filename='log/tgs_server_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Read the key shared between Authentication Server and Ticket-Granting Server from file
with open('db/auth_server_key.txt', 'r') as key_file:
    tgs_shared_key = key_file.read().strip()


def generate_ticket(username, client_key, expiration_time):
    # Generate a secure ticket containing user information
    ticket_data = {
        'username': username,
        'expiration_time': expiration_time.isoformat(),
        'client_key': client_key
    }
    return json.dumps(ticket_data).encode()
def tgs_handler(client_socket, tgt):
    try:
        tgt_data = json.loads(tgt.decode())
        username = tgt_data.get('username', '')
        client_key = tgt_data.get('client_key', '')
        expiration_time = datetime.fromisoformat(tgt_data.get('expiration_time', ''))

        # Check if the TGT is still valid
        if datetime.now() <= expiration_time:
            # Generate and send a session token (Service Ticket) to the client
            session_token = generate_ticket(username, client_key, expiration_time)
            client_socket.send(session_token)
            logging.info("TGS request handled successfully.")

        else:
            # TGT has expired
            logging.warning(f"TGT expired for user: {username}")
            client_socket.send(b'TGT expired')

    except Exception as e:
        logging.error(f"Error handling TGS request: {e}")
        client_socket.send(b'Error processing TGS request')

    finally:
        client_socket.close()

def tgs_server():
    # Set up the server socket
    server_host = '127.0.0.1'
    server_port = 12346
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Create an SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='cert/tgs_server.crt', keyfile='cert/tgs_server.key')


    # Wrap the server socket with SSL/TLS
    server_socket = ssl_context.wrap_socket(server_socket, server_side=True)

    server_socket.bind((server_host, server_port))
    server_socket.listen(5)

    logging.info(f"[*] Ticket-Granting Server listening on {server_host}:{server_port}")

    try:
        while True:
            # Accept incoming connections
            client_socket, addr = server_socket.accept()
            logging.info(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

            # Receive Ticket-Granting Ticket (TGT) from the client
            tgt = client_socket.recv(1024)
            if not tgt:
                continue

            # Handle TGS request in a new thread
            tgs_handler_thread = threading.Thread(target=tgs_handler, args=(client_socket, tgt))
            tgs_handler_thread.start()

    except KeyboardInterrupt:
        logging.info("\n[*] Ticket-Granting Server shutting down.")
    finally:
        server_socket.close()

def handle_tgs_request(client_socket, tgt):
    # Handle the TGS request in a separate function to run in a new thread
    try:
        # Decrypt TGT using the key shared between Authentication Server and Ticket-Granting Server
        session_token = tgs_handler(tgt, tgs_shared_key)

        # Send the session token (Service Ticket) to the client
        client_socket.send(session_token)
        logging.info("TGS request handled successfully.")

    except Exception as e:
        logging.error(f"Error handling TGS request: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    tgs_server()