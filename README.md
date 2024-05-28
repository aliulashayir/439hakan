# Kerberos
This is a simplified implementation of the Kerberos IBM system.

## System Overview
The system consists of three main components:

### Authentication Server (`auth_server.py`)
- Listens for incoming connections from clients.
- Validates client credentials (username and hashed password) against stored user credentials.
- If authentication is successful, generates a Ticket-Granting Ticket (TGT) containing user information and expiration time.
- Sends the TGT to the client for future interactions with other servers.

### Ticket-Granting Server (`tgs_server.py`)
- Listens for incoming connections from clients.
- Receives a Ticket-Granting Ticket (TGT) from clients after successful authentication with the Authentication Server.
- Validates the TGT and, if valid, generates a session token (Service Ticket) with user information.
- Sends the session token to the client, allowing access to the Time Server.

### Time Server (`time_server.py`)
- Listens for incoming connections from clients.
- Receives a session token from clients after successful validation by the Ticket-Granting Server.
- Validates the session token and, if valid, responds with the current time.

### Key Management Script (`update.py`)
- Provides an interface for updating server keys and the admin password.
- Requires authentication of the administrator before allowing updates.
- Logs all key update activities for auditing purposes.

## Design Choices

### Security Measures
- User passwords are hashed using the SHA-256 algorithm for storage and comparison.
- Server keys are randomly generated and stored securely.

### Concurrency
- Each server (Auth Server, TGS Server, Time Server) is designed to handle multiple concurrent client connections using threading.

### SSL/TLS Encryption
- SSL/TLS is implemented for secure communication between servers and clients.
- Certificates and keys are used to establish secure connections.

### Logging
- Extensive logging is implemented to track server activities, key updates, and authentication events.
- Log files are created for each server, and a key management log records key update activities.




##IN THE FUTURE
- Planning on building a more robust real world like solution with Django or Java Spring Boot
- On top of SSL/TLS extra security futures like JWT would be even better
