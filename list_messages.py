# list_message.py

import socket
import threading
import sys
from datetime import datetime

PORT = 5050
SERVER = "localhost"  # Change to server's IP if running remotely
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

def get_current_time():
    """Returns the current time formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def connect():
    """Establishes a socket connection to the server."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        return client
    except Exception as e:
        print(f"\033[1;31m[ERROR] Unable to connect to the server: {e}\033[0m")
        sys.exit()

def receive(client):
    """Continuously listens for messages from the server and displays them."""
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if not message:
                print("\033[1;31m[INFO] Server closed the connection.\033[0m")
                break

            # Display the incoming message with formatting
            print(f"\033[1;34m{message}\033[0m")  # Blue color for incoming messages
        except Exception as e:
            print(f"\033[1;31m[ERROR] {e}\033[0m")
            break

    print('\033[1;33mDisconnected from the server.\033[0m')  # Yellow color
    client.close()
    sys.exit()

def start():
    """Connects to the server and starts listening for messages."""
    # Prompt for username
    username = input('Enter your username (for receiving private messages): ').strip()
    while not username:
        username = input("Username cannot be empty. Enter your username: ").strip()

    # Establish connection
    connection = connect()

    # Send username to the server
    try:
        connection.sendall(username.encode(FORMAT))
    except Exception as e:
        print(f"\033[1;31m[ERROR] Failed to send username: {e}\033[0m")
        connection.close()
        sys.exit()

    # Start a thread to handle incoming messages
    receive_thread = threading.Thread(target=receive, args=(connection,))
    receive_thread.daemon = True  # Ensure the thread exits when the main program exits
    receive_thread.start()

    print("\033[1;32mListening for messages. Press Ctrl+C to disconnect.\033[0m\n")

    try:
        while True:
            # Keep the main thread alive to listen for incoming messages
            receive_thread.join(1)
    except (KeyboardInterrupt, EOFError):
        print('\n\033[1;33mDisconnecting from the server...\033[0m')
        try:
            connection.sendall(DISCONNECT_MESSAGE.encode(FORMAT))
        except:
            pass
        connection.close()
        sys.exit()


    start()
