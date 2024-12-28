
import socket

import select


HEADER_LENGTH = 10

IP = "127.0.0.1"

PORT = 1234


# Create a socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Allow the socket to reuse the address

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# Bind to the specified IP and port

server_socket.bind((IP, PORT))


# Listen for incoming connections

server_socket.listen()


# List of sockets for select.select()

sockets_list = [server_socket]


# List of connected clients

clients = {}


print(f'Server started on {IP}:{PORT}')


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

    except:

        return False


while True:

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


            print(f'New connection from {client_address} with username: {user["data"].decode("utf-8")}')

        else:

            # Handle incoming messages from an existing client

            message = receive_message(notified_socket)

            if message is False:

                print(f'Connection closed from: {clients[notified_socket]["data"].decode("utf-8")}')

                sockets_list.remove(notified_socket)

                del clients[notified_socket]

                continue


            # Get the username of the client who sent the message

            user = clients[notified_socket]


            # Print the received message on the server

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')


            # Forward the message to all other connected clients

            for client_socket in clients:

                if client_socket != notified_socket:

                    # Send the message to other clients, prefixed with the sender's username

                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])


    # Handle exceptions (client disconnects)

    for notified_socket in exception_sockets:

        sockets_list.remove(notified_socket)

        del clients[notified_socket]



import socket

import threading

import tkinter as tk

from tkinter import messagebox


HEADER_LENGTH = 10

IP = "127.0.0.1"

PORT = 1234


# Create a socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Connect to the server

def connect_to_server():

    try:

        client_socket.connect((IP, PORT))  # Connect to server

        print("Connected to the server.")  # Debugging statement to confirm connection

        username = input("Enter your username: ")  # Prompt for username input

        username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')

        client_socket.send(username_header + username.encode('utf-8'))

        print("Username sent to the server.")  # Debugging statement to confirm username sent

        threading.Thread(target=receive_messages, daemon=True).start()  # Start background thread to receive messages

    except Exception as e:

        print(f"Error while connecting: {e}")

        messagebox.showerror("Connection Error", f"Unable to connect to server. Error: {e}")


# Function to receive messages from the server

def receive_messages():

    while True:

        try:

            message_header = client_socket.recv(HEADER_LENGTH)

            if not len(message_header):  # If no header is received, the server has closed the connection

                print("Server disconnected.")

                break


            message_length = int(message_header.decode('utf-8').strip())

            message = client_socket.recv(message_length).decode('utf-8')

            print(f"Received message: {message}")  # Debugging statement to check incoming messages

            display_message(message)

        except Exception as e:

            print(f"Error receiving message: {e}")

            break


# Function to display the received message in the GUI

def display_message(message):

    text_area.config(state=tk.NORMAL)  # Enable editing the text area

    text_area.insert(tk.END, f"{message}\n")

    text_area.yview(tk.END)  # Auto-scroll to the bottom

    text_area.config(state=tk.DISABLED)  # Make it read-only again


# Function to send messages to the server

def send_message():

    message = message_input.get()

    if message:

        try:

            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')

            client_socket.send(message_header + message.encode('utf-8'))

            print(f"Message sent: {message}")  # Debugging statement to check sent messages

            display_message(f"You: {message}")

            message_input.delete(0, tk.END)  # Clear input field

        except:

            messagebox.showerror("Connection Error", "Could not send message.")


# Setting up the Tkinter GUI

def setup_gui():

    global root, text_area, message_input

    root = tk.Tk()

    root.title("Chat Application - Client")


    # Chat area

    text_area = tk.Text(root, height=20, width=50, wrap=tk.WORD)

    text_area.pack(padx=10, pady=10)

    text_area.config(state=tk.DISABLED)  # Make it read-only initially


    # Message input

    message_input = tk.Entry(root, width=40)

    message_input.pack(side=tk.LEFT, padx=10, pady=10)


    # Send button

    send_button = tk.Button(root, text="Send", width=10, command=send_message)

    send_button.pack(side=tk.LEFT, padx=10)


    # Connect to server button

    connect_button = tk.Button(root, text="Connect to Server", command=connect_to_server)

    connect_button.pack(side=tk.LEFT, padx=10)


    root.mainloop()


if _name_ == "_main_":

    setup_gui