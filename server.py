import socket
import select
import os
from error_handling import setup_logging, log_error, log_info, log_warning

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

# Initialize logging
setup_logging()

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow the socket to reuse the address
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    # Bind to the specified IP and port
    server_socket.bind((IP, PORT))
    log_info(f"Server started on {IP}:{PORT}")
except Exception as e:
    log_error(f"Error binding server socket: {e}")
    exit()

# Listen for incoming connections
server_socket.listen()

# List of sockets for select.select()
sockets_list = [server_socket]

# List of connected clients
clients = {}

# Function to handle receiving messages from a client
def receive_message(client_socket):
    try:
        # Receive message header (size of the message)
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False

        # Get the length of the message
        message_length = int(message_header.decode('utf-8').strip())

        # Return the message header and the actual message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}
    except Exception as e:
        log_error(f"Error receiving message from {client_socket}: {e}")
        return False

# Function to handle receiving a file
def receive_file(client_socket):
    try:
        # Receive the file name
        file_header = client_socket.recv(HEADER_LENGTH)
        if not len(file_header):
            return False

        file_length = int(file_header.decode('utf-8').strip())
        file_name = client_socket.recv(file_length).decode('utf-8')

        # Receive the file size
        file_header = client_socket.recv(HEADER_LENGTH)
        file_size = int(file_header.decode('utf-8').strip())

        # Receive the file content in chunks
        with open(f"received_files/{file_name}", 'wb') as file:
            while file_size > 0:
                chunk = client_socket.recv(min(file_size, 4096))
                file.write(chunk)
                file_size -= len(chunk)

        log_info(f"File {file_name} received successfully.")
        return file_name
    except Exception as e:
        log_error(f"Error receiving file from {client_socket}: {e}")
        return False

while True:
    try:
        # Use select to handle multiple clients
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_sockets:
            # If the server socket is notified, it means a new connection is being made
            if notified_socket == server_socket:
                # Accept the new client connection
                client_socket, client_address = server_socket.accept()

                # Receive the client's username
                user = receive_message(client_socket)
                if user is False:
                    continue

                # Add the new client to the list of sockets and clients
                sockets_list.append(client_socket)
                clients[client_socket] = user

                log_info(f'New connection from {client_address} with username: {user["data"].decode("utf-8")}')
            else:
                # Handle incoming messages from an existing client
                message = receive_message(notified_socket)
                if message is False:
                    log_info(f'Connection closed from: {clients[notified_socket]["data"].decode("utf-8")}')
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue

                # Check if the message is a file transfer
                if message['data'].decode('utf-8') == "FILE":
                    # Receive file name
                    file_name_header = notified_socket.recv(HEADER_LENGTH)
                    file_name_length = int(file_name_header.decode('utf-8').strip())
                    file_name = notified_socket.recv(file_name_length).decode('utf-8')
                    # Receive file size
                    file_size_header = notified_socket.recv(HEADER_LENGTH)
                    file_size_length = int(file_size_header.decode('utf-8').strip())
                    file_size = int(notified_socket.recv(file_size_length).decode('utf-8'))
                    # Receive file content
                    received = 0
                    file_content = b""
                    while received < file_size:
                        chunk = notified_socket.recv(min(4096, file_size - received))
                        if not chunk:
                            break
                        file_content += chunk
                        received += len(chunk)
                    # Relay file to other clients
                    dead_clients = []
                    for client_socket in clients:
                        if client_socket != notified_socket:
                            try:
                                client_socket.send(
                                    clients[notified_socket]['header'] + clients[notified_socket]['data'] +
                                    message['header'] + message['data']
                                )
                                client_socket.send(file_name_header + file_name.encode('utf-8'))
                                client_socket.send(file_size_header + str(file_size).encode('utf-8'))
                                # Send file content in chunks
                                sent = 0
                                while sent < len(file_content):
                                    chunk = file_content[sent:sent+4096]
                                    client_socket.send(chunk)
                                    sent += len(chunk)
                            except Exception as e:
                                log_error(f"Error sending file to {clients[client_socket]['data'].decode('utf-8')}: {e}")
                                dead_clients.append(client_socket)
                    # Remove dead clients
                    for dc in dead_clients:
                        sockets_list.remove(dc)
                        del clients[dc]

                else:
                    # Relay normal messages
                    dead_clients = []
                    for client_socket in clients:
                        if client_socket != notified_socket:
                            try:
                                client_socket.send(
                                    clients[notified_socket]['header'] + clients[notified_socket]['data'] +
                                    message['header'] + message['data']
                                )
                            except Exception as e:
                                log_error(f"Error sending message to {clients[client_socket]['data'].decode('utf-8')}: {e}")
                                dead_clients.append(client_socket)
                    for dc in dead_clients:
                        sockets_list.remove(dc)
                        del clients[dc]

        # Handle exceptions (client disconnects)
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]

    except Exception as e:
        log_error(f"Unexpected server error: {e}")

