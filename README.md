**Real-Time Chat Application** 💬✨
**Overview**
This is a real-time chat application with a modern GUI featuring chat bubbles, supporting text messaging and file transfers between multiple clients connected to a server.

**Features** 🚀
Real-time messaging with a user-friendly bubble interface 💬
File transfer support with chunked uploads/downloads 📁
Multiple client handling via socket programming and select
Robust error handling and logging for stable operation 🛠️
Simple username-based login for user identification 👤

**Getting Started** ⚙️
Server Setup
Run server.py to start the chat server.
Server listens on 127.0.0.1:1234 by default.
Logs are saved to server.log for debugging and monitoring.

**Client Setup**
Run client.py to launch the GUI chat client.
Enter your username and start chatting!

**Planned Improvements** 🌟
🔐 Authentication & User Management: Secure login, registration, and roles.
🔒 Encryption & Integrity Checks: Secure communication with TLS/SSL and message validation.
💬 Emoji Support: Add emojis 😄🎉 to chat bubbles for richer conversations.
🖼️ GUI Enhancements: Typing indicators, read receipts, themes, and more.
⚙️ Scalability: Optimize server for more users and robust deployment.

**Folder Structure**📁
real-time-chat-app/
│
├── server.py                # Main server-side script
├── client.py                # Client-side GUI chat application
├── error_handling.py        # Logging and error handling utilities
│
├── received_files/          # Directory where received files are stored
│
├── README.md                # Project documentation (your README)
│
└── requirements.txt         # List of Python dependencies (optional)


**Usage Tips** 💡
Files are saved in a received_files/ directory.
Use consistent usernames for easier tracking in logs.
Check server.log for detailed error and info messages.

**Dependencies**📦
Python 3.x
Standard libraries: socket, select, tkinter, logging, os

**Contact & Support**📬
For questions or contributions, please reach out or open an issue on the project repo.

**Enjoy chatting!** 🎉💬
