import socket
import json
import time
import ssl
import getpass

def send_credentials_to_as(username):
    auth_server_host = '127.0.0.1'
    auth_server_port = 12345

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    auth_client_socket = ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    
    try:
        auth_client_socket.connect((auth_server_host, auth_server_port))

        # Securely get the password from the command line
        password = getpass.getpass("Enter your password: ")

        # Send the username and password to the Authentication Server
        credentials = json.dumps({'username': username, 'password': password}).encode()
        auth_client_socket.send(credentials)

        tgt = auth_client_socket.recv(1024)
        return tgt

    finally:
        auth_client_socket.close()

def send_tgt_to_tgs(tgt):
    tgs_server_host = '127.0.0.1'
    tgs_server_port = 12346
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    tgs_client_socket = ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    
    try:
        tgs_client_socket.connect((tgs_server_host, tgs_server_port))

        # Send the Ticket-Granting Ticket (TGT) to the Ticket-Granting Server
        tgs_client_socket.send(tgt)

        # Introduce a delay (simulating processing time)
        time.sleep(1)

        # Receive the session token (Service Ticket) from the Ticket-Granting Server
        session_token = tgs_client_socket.recv(1024)
        return session_token

    except Exception as e:
        print(f"[!] Error in send_tgt_to_tgs: {e}")
        return b'Error in send_tgt_to_tgs'

    finally:
        tgs_client_socket.close()
def send_session_token_to_time_server(session_token):
    time_server_host = '127.0.0.1'
    time_server_port = 12347

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    time_client_socket = ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    try:
        time_client_socket.connect((time_server_host, time_server_port))

        # Send the session token to the Time Server
        time_client_socket.send(session_token)

        # Receive the response from the Time Server
        response = time_client_socket.recv(1024)
        print(response.decode())

    except Exception as e:
        print(f"[!] Error in send_session_token_to_time_server: {e}")

    finally:
        time_client_socket.close()

if __name__ == "__main__":
    # Get username from the command line
    username = input("Enter your username: ")

    # Step 1: Get the Ticket-Granting Ticket (TGT) from the Authentication Server
    tgt = send_credentials_to_as(username)

    if tgt == b'Invalid credentials':
        print("Authentication failed. Invalid credentials.")
    elif tgt == b'TGT expired':
        print("Authentication failed. Ticket-Granting Ticket (TGT) expired.")
    else:
        print("Authentication successful. Proceeding to get the session token.")

        # Step 2: Get the session token from the Ticket-Granting Server
        session_token = send_tgt_to_tgs(tgt)

        if session_token == b'TGT expired':
            print("Authentication failed. Ticket-Granting Ticket (TGT) expired.")
        elif session_token == b'Session token expired':
            print("Access denied. Session token expired.")
        else:
            print("Access granted. Proceeding to access the Time Server.")

            # Step 3: Access the Time Server with the session token
            send_session_token_to_time_server(session_token)
