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

def send(client, msg):
    """Sends a message to the server after encoding it."""
    try:
        message = msg.encode(FORMAT)
        client.sendall(message)
    except Exception as e:
        print(f"\033[1;31m[ERROR] Failed to send message: {e}\033[0m")

def receive(client, username):
    """Continuously listens for messages from the server and displays them."""
    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if not message:
                print("\033[1;31m[INFO] Server closed the connection.\033[0m")
                break

            # Clear the current input line
            print("\r" + " " * 80, end="")  # Adjust the number for your terminal width

            # Display the incoming message
            print(f"\033[1;34m{message}\033[0m")

            # Reprint the input prompt
            print(f"\033[1;32m{username}:\033[0m ", end="", flush=True)
        except Exception as e:
            print(f"\033[1;31m[ERROR] {e}\033[0m")
            break

    print('\033[1;33mDisconnected from the server.\033[0m')
    sys.exit()

def start():
    """Manages user interaction, connects to the server, and handles sending/receiving messages."""
    # Prompt for username
    username = input('Enter your username: ').strip()
    while not username:
        username = input("Username cannot be empty. Enter your username: ").strip()

    answer = input(f'Would you like to connect with username "{username}"? (yes/no): ').strip().lower()
    if answer != 'yes':
        print("Connection aborted by the user.")
        sys.exit()

    # Establish connection
    connection = connect()

    # Send username to the server
    send(connection, username)

    # Start a thread to handle incoming messages
    receive_thread = threading.Thread(target=receive, args=(connection, username))
    receive_thread.daemon = True  # Ensure the thread exits when the main program exits
    receive_thread.start()

    print("\033[1;32mYou can start sending messages. Type 'q' to quit.\033[0m\n")

    while True:
        try:
            msg = input(f"\033[1;32m{username}:\033[0m ").strip()

            if msg.lower() == 'q':
                send(connection, DISCONNECT_MESSAGE)
                break

            if msg:
                send(connection, msg)
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or Ctrl+D gracefully
            send(connection, DISCONNECT_MESSAGE)
            break
        except Exception as e:
            print(f"\033[1;31m[ERROR] {e}\033[0m")
            break

    print('\033[1;33mDisconnected\033[0m')  # Display disconnect message in yellow
    connection.close()
    sys.exit()

if __name__ == "__main__":
    start()
