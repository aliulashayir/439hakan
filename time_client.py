import socket

def connect_to_time_server():
    # Set up the client socket
    server_host = '127.0.0.1'
    server_port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the Time Server
        client_socket.connect((server_host, server_port))
        print(f"[*] Connected to {server_host}:{server_port}")

        # Receive and print the current time from the server
        data = client_socket.recv(1024)
        print(f"[*] Received from server: {data.decode()}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    connect_to_time_server()
