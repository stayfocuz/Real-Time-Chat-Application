import socket
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import logging
import os

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

# Set up logging
logging.basicConfig(filename='client.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
def connect_to_server():
    try:
        username = username_input.get().strip()
        if not username:
            messagebox.showerror("Input Error", "Please enter a username.")
            return
        client_socket.connect((IP, PORT))  # Connect to server
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(username_header + username.encode('utf-8'))
        logging.info(f"Username sent to the server: {username}")
        connect_button.config(state=tk.DISABLED)
        username_input.config(state=tk.DISABLED)
        threading.Thread(target=receive_messages, daemon=True).start()  # Start background thread to receive messages
    except Exception as e:
        logging.error(f"Error while connecting to server: {e}")
        messagebox.showerror("Connection Error", f"Unable to connect to server. Error: {e}")

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                break
            username_length = int(username_header.decode('utf-8').strip())
            sender = client_socket.recv(username_length).decode('utf-8')
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                break
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            if message == "FILE":
                # Receive file name
                file_name_header = client_socket.recv(HEADER_LENGTH)
                file_name_length = int(file_name_header.decode('utf-8').strip())
                file_name = client_socket.recv(file_name_length).decode('utf-8')
                # Receive file size
                file_size_header = client_socket.recv(HEADER_LENGTH)
                file_size_length = int(file_size_header.decode('utf-8').strip())
                file_size = int(client_socket.recv(file_size_length).decode('utf-8'))
                # Receive file content
                received = 0
                file_path = f"received_{file_name}"
                with open(file_path, "wb") as f:
                    while received < file_size:
                        chunk = client_socket.recv(min(4096, file_size - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                # Show "Received a file: ..." above the bubble, icon and file name inside
                display_message(file_name, sender=sender, file_received=True, file_path=file_path)
            else:
                display_message(message, sender=sender, self_message=False)
        except Exception as e:
            break

# Add this method to Canvas for rounded rectangles
def _create_round_rectangle(self, x1, y1, x2, y2, r=20, **kwargs):
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y1+r,
        x1, y1
    ]
    return self.create_polygon(points, smooth=True, **kwargs)
tk.Canvas.create_round_rectangle = _create_round_rectangle

def display_message(message, sender=None, self_message=False, file_sent=False, file_received=False, file_path=None):
    is_self = self_message or (sender == username_input.get())
    bubble_color = "#e0f7fa" if is_self else "#fff9c4"
    text_color = "black"
    x_pad = 10
    y_pad = 5
    max_width = 200
    font = ("Arial", 11)

    # Calculate text size (for file, show icon and name)
    display_text = message
    if file_sent or file_received:
        display_text = f"📄 {message}"

    text_id = chat_canvas.create_text(0, 0, text=display_text, font=font, fill=text_color, anchor="nw", width=max_width)
    bbox = chat_canvas.bbox(text_id)
    chat_canvas.delete(text_id)
    width = bbox[2] - bbox[0] + 20
    height = bbox[3] - bbox[1] + 10

    y = chat_canvas.bbox("all")[3] + y_pad if chat_canvas.bbox("all") else y_pad
    if is_self:
        canvas_width = chat_canvas.winfo_width()
        if canvas_width <= 1:  # Not yet rendered, fallback to configured width
            canvas_width = int(chat_canvas['width'])
        x = canvas_width - width - x_pad
    else:
        x = x_pad

    r = 20

    # Add "sent", "file sent", or "from: sender"/"Received a file" above the bubble
    if file_sent:
        chat_canvas.create_text(x + width, y, text="file sent", font=("Arial", 9, "italic"), fill="#4682b4", anchor="ne")
        y += 16
    elif file_received:
        chat_canvas.create_text(x, y, text=f"Received a file: {message}", font=("Arial", 9, "italic"), fill="#555", anchor="nw")
        y += 16
    elif is_self:
        chat_canvas.create_text(x + width, y, text="sent", font=("Arial", 9, "italic"), fill="#4682b4", anchor="ne")
        y += 16
    elif sender:
        chat_canvas.create_text(x, y, text=f"from: {sender}", font=("Arial", 9, "italic"), fill="#555", anchor="nw")
        y += 16

    # Draw the bubble
    bubble = chat_canvas.create_round_rectangle(x, y, x + width, y + height, r, fill=bubble_color, outline="", width=0)
    text_item = chat_canvas.create_text(x + 10, y + 5, text=display_text, font=font, fill=text_color, anchor="nw", width=max_width)

    # If received file, make the bubble clickable to view the file
    if file_received and file_path:
        def open_file(event, path=file_path):
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Open File", f"Could not open file: {e}")
        chat_canvas.tag_bind(bubble, "<Button-1>", open_file)
        chat_canvas.tag_bind(text_item, "<Button-1>", open_file)
        chat_canvas.itemconfig(bubble, fill="#b2ebf2")  # Slightly different color on hover/click

    chat_canvas.config(scrollregion=chat_canvas.bbox("all"))
    chat_canvas.yview_moveto(1.0)

# Function to send messages to the server
def send_message():
    message = message_input.get()
    if message and message != "Type here":
        try:
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message.encode('utf-8'))
            # Show sent message (right side, with "sent" above)
            display_message(message, sender=username_input.get(), self_message=True)
            message_input.delete(0, tk.END)  # Clear input field
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            messagebox.showerror("Connection Error", "Set your username first.")

# Function to send a file to the server
def send_file():
    file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
    if file_path:
        try:
            file_name = os.path.basename(file_path)
            # Send "FILE" indicator
            file_indicator = "FILE"
            file_indicator_header = f"{len(file_indicator):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(file_indicator_header + file_indicator.encode('utf-8'))
            # Send file name
            file_name_header = f"{len(file_name):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(file_name_header + file_name.encode('utf-8'))
            # Send file size
            file_size = os.path.getsize(file_path)
            file_size_str = str(file_size)
            file_size_header = f"{len(file_size_str):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(file_size_header + file_size_str.encode('utf-8'))
            # Send file content
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(4096)
                    if not chunk:
                        break
                    client_socket.send(chunk)
            # Show "file sent" above the bubble, icon and file name inside
            display_message(file_name, sender=username_input.get(), self_message=True, file_sent=True)
        except Exception as e:
            logging.error(f"Error sending file: {e}")
            messagebox.showerror("File Error", f"Could not send file: {e}")

# Setting up the Tkinter GUI
def setup_gui():
    global root, chat_canvas, message_input, username_input, connect_button
    root = tk.Tk()
    root.title("Chat Application - Client UI")
    root.geometry("450x600")
    root.resizable(False, False)

    # Header
    header = tk.Frame(root, bg="#4682b4", height=50)
    header.pack(fill=tk.X)
    tk.Label(header, text="Real Time Chat", bg="#4682b4", fg="white", font=('Arial', 16, 'bold')).pack(fill=tk.BOTH, expand=True, pady=10)

    # Username input and connect button
    user_frame = tk.Frame(root)
    user_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
    tk.Label(user_frame, text="Username:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)  # Bold font
    username_input = tk.Entry(user_frame, width=22, font=('Arial', 10))
    username_input.pack(side=tk.LEFT, padx=(5, 0))
    username_input.insert(0, "Type username here")  # Placeholder text

    def on_username_click(event):
        if username_input.get() == "Type username here":
            username_input.delete(0, tk.END)
            username_input.config(fg="black")

    def on_username_focusout(event):
        if username_input.get() == "":
            username_input.insert(0, "Type username here")
            username_input.config(fg="grey")

    username_input.bind('<FocusIn>', on_username_click)
    username_input.bind('<FocusOut>', on_username_focusout)
    username_input.config(fg="grey")

    connect_button = tk.Button(user_frame, text="Connect", command=connect_to_server, font=('Arial', 10, 'bold'))
    connect_button.pack(side=tk.LEFT, padx=(10, 0))

    # Chat area
    chat_frame = tk.Frame(root, bg="#87ceeb")
    chat_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(10, 0))
    chat_canvas = tk.Canvas(chat_frame, bg="#87ceeb", highlightthickness=0, width=380, height=400)
    chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(chat_frame, command=chat_canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_canvas.configure(yscrollcommand=scrollbar.set)

    # Input area at the bottom
    input_frame = tk.Frame(root)
    input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    message_input = tk.Entry(
        input_frame,
        width=25,  # Reduce width to make space
        font=('Arial', 12),
        relief="sunken",
        bd=3,
        justify="left"  # Left align the text
    )
    message_input.pack(side=tk.LEFT, padx=(0, 10), ipady=6)
    message_input.insert(0, "Type here")  # Capital T

    def on_entry_click(event):
        if message_input.get() == "Type here":
            message_input.delete(0, tk.END)
            message_input.config(fg="black")

    def on_focusout(event):
        if message_input.get() == "":
            message_input.insert(0, "Type here")
            message_input.config(fg="grey")

    message_input.bind('<FocusIn>', on_entry_click)
    message_input.bind('<FocusOut>', on_focusout)
    message_input.config(fg="grey")

    send_button = tk.Button(
        input_frame,
        text="Send",
        width=7,
        command=send_message,
        font=('Arial', 10, 'bold'),
        bg="#4682b4",
        fg="white",
        activebackground="#5a9bd4",
        activeforeground="white"
    )
    send_button.pack(side=tk.LEFT, padx=(0, 5))

    send_file_button = tk.Button(
        input_frame,
        text="Send File",
        width=15,
        command=send_file,
        font=('Arial', 10, 'bold'),
        bg="#4682b4",
        fg="white",
        activebackground="#5a9bd4",
        activeforeground="white"
    )
    send_file_button.pack(side=tk.LEFT, padx=(10, 5))

    root.mainloop()

if __name__ == "__main__":
    setup_gui()

