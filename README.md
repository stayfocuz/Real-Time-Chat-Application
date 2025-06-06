# Real-Time-Chat-Application
🗨️ Python Chat Application (Client-Server Model)
This is a simple Python-based chat application demonstrating the use of sockets, multi-threading, and a Tkinter GUI. The application allows multiple clients to connect to a server and exchange messages in real time.

📁 Project Structure
chat_app/
│
├── server.py           # TCP Server handling multiple clients using select
├── client.py           # GUI-based client application using Tkinter
└── README.md           # Project documentation

🧰 Features
✅ Real-time chat between multiple clients
✅ GUI interface for the client using Tkinter
✅ Socket programming with select for handling multiple connections
✅ Multi-threading to receive messages in the background
✅ Basic username identification
✅ Message formatting and broadcasting

🚀 How It Works
Server Side (server.py)
Creates a TCP socket and listens for incoming client connections.
Handles multiple clients using the select module.
Accepts a username from each client upon connection.
Forwards messages received from any client to all others.

Client Side (client.py)
GUI built with Tkinter.
Prompts for a username when connecting.
Allows the user to send and receive messages in a chat window.
Uses threading to receive messages without freezing the GUI.

💻 Requirements
Python 3.x
Works on Windows, Linux, and macOS
No external libraries required

🔧 How to Run
1. Clone the repository
git clone https://github.com/yourusername/chat_app.git
cd chat_app
2. Start the Server
python server.py
The server will start and listen on 127.0.0.1:1234.
3. Start the Client
Open another terminal (or multiple terminals for multiple clients):
python client.py
Click the "Connect to Server" button and enter your username in the terminal.

You can now chat with others connected to the same server.

🧪 Example
Run server.py:
Server started on 127.0.0.1:1234
Run client.py, click "Connect to Server", and enter a username.
Send messages using the input field and see them broadcasted to all clients.

🛠️ Code Highlights
Message Structure
Each message is sent with a fixed-length header (10 bytes), indicating the length of the actual message. This ensures correct parsing of stream data:
HEADER_LENGTH = 10
message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')

Select-based Server
Efficient handling of multiple clients using:
read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

Threaded Client Receiver
Prevents GUI from freezing during message reception:
threading.Thread(target=receive_messages, daemon=True).start()

⚠️ Notes
This is a basic implementation intended for educational purposes.
It does not use encryption or authentication.
For production use, consider using more robust frameworks like WebSockets, asyncio, or TLS for secure connections.

📌 TODO (Optional Enhancements)
Add support for private messaging (DMs)
Improve UI/UX with emojis and themes
Add file transfer capability
Encrypt messages using SSL/TLS
Save chat history

👨‍💻 Authors
Developed by John Kyle B. Cuarteros
Contributions welcome!

📜 License
This project is open-source and available under the MIT License.
