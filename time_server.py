import socket
import ssl
import logging
import json
from datetime import datetime

# Configure logging
LOG_FILE = 'log/time_server.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_session_token(session_token):
    try:
        session_data = json.loads(session_token.decode())
        username = session_data.get('username', '')
        expiration_time = datetime.fromisoformat(session_data.get('expiration_time', ''))

        if datetime.now() <= expiration_time:
            return True
        else:
            logging.warning(f"Session token expired for user: {username}")
            return False

    except Exception as e:
        logging.error(f"Error validating session token: {e}")
        return False

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024)
        if not data:
            return

        session_token = data

        if validate_session_token(session_token):
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            client_socket.send(current_time.encode())
            logging.info("Time information sent successfully")
        else:
            client_socket.send(b'Session token expired')
            logging.warning("Session token validation failed")

    except Exception as e:
        print(f"[!] Error handling client: {e}")
        logging.error(f"Error handling client: {e}")
    finally:
        client_socket.close()

def time_server():
    server_host = '127.0.0.1'
    server_port = 12347
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='cert/time_server.crt', keyfile='cert/time_server.key')

    server_socket = ssl_context.wrap_socket(server_socket, server_side=True)

    server_socket.bind((server_host, server_port))
    server_socket.listen(5)

    logging.info(f"[*] Time Server listening on {server_host}:{server_port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            logging.info(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
            handle_client(client_socket)
    except KeyboardInterrupt:
        logging.info("\n[*] Time Server shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    print("Time Server is running. Press Ctrl+C to shut down.")
    time_server()
