import socket
import select
from prettytable import PrettyTable

# Define server port and IP address
SERVER_PORT = 7777
SERVER_IP = "0.0.0.0"

# Create a PrettyTable for displaying client information
socket_table = PrettyTable(["client name", "socket"])
clients = {}  # Dictionary to store client names and their corresponding sockets


def print_names():
    """
    Function to print the list of connected client names to all clients.
    """
    names = list(clients.keys())
    for client in clients.values():
        try:
            client.sendall(f"CONNECTED_NAMES {' '.join(names)}\n".encode())
        except Exception as e:
            print(f"Error broadcasting names: {e}")


def handle_client_request(current_socket, data):
    """
    Function to handle different client requests such as NAME, GET_NAMES, MSG, and EXIT.
    """
    reply = None
    dest_socket = None

    try:
        parts = data.split(' ', 2)  # Split the incoming data into command and arguments
        command = parts[0]
        args = parts[1:]

        if command == 'NAME':
            if len(args) != 1:
                return "ERROR Invalid NAME command\n", current_socket

            new_name = args[0]
            if new_name in clients:
                return "ERROR Duplicate name\n", current_socket
            else:
                old_name = None
                for name, sock in clients.items():
                    if sock == current_socket:
                        old_name = name
                        break
                if old_name:
                    del clients[old_name]
                clients[new_name] = current_socket
                print_names()
                return None, None

        elif command == 'GET_NAMES':
            names = list(clients.keys())
            return f"NAMES {' '.join(names)}\n", current_socket

        elif command == 'MSG':
            if len(args) != 2:
                return "ERROR Invalid MSG command\n", current_socket

            target_name, message = args
            if target_name in clients:
                dest_socket = clients[target_name]
                reply = f"MSG_FROM {get_client_name(current_socket)} {message}\n"
                return reply, dest_socket
            else:
                return "ERROR No such client\n", current_socket

        elif command == 'EXIT':
            return None, None

        else:
            return "ERROR Invalid command\n", current_socket
    except Exception as e:
        print(f"Error handling request from client: {e}")
        return "ERROR Processing request\n", current_socket


def get_client_name(client_socket):
    """
    Function to retrieve the client name associated with a given socket.
    """
    for name, sock in clients.items():
        if sock == client_socket:
            return name
    return None


def main():
    """
    Main function to set up and run the server.
    """
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    server_socket.bind((SERVER_IP, SERVER_PORT))  # Bind the socket to the IP address and port
    server_socket.listen()  # Listen for incoming connections
    print("Listening for clients...")
    client_sockets = []  # List to keep track of connected client sockets
    messages_to_send = []  # List to keep track of messages to send

    try:
        while True:
            # Prepare the list of sockets to be checked for readability and writability
            read_list = client_sockets + [server_socket]
            ready_to_read, ready_to_write, in_error = select.select(read_list, client_sockets, [])

            for current_socket in ready_to_read:
                if current_socket is server_socket:
                    # Handle new client connections
                    client_socket, client_address = server_socket.accept()
                    print("Client joined!\n", client_address)
                    client_sockets.append(client_socket)
                else:
                    try:
                        data = current_socket.recv(1024).decode().strip()  # Receive data from the client
                        if not data:
                            raise Exception("Connection closed")

                        response, dest_socket = handle_client_request(current_socket, data)  # Handle client request
                        if response and not dest_socket:  # if the sender does not have a socket to send the data
                            # (msg to himself)
                            messages_to_send.append((current_socket, response))
                        if dest_socket and response:
                            messages_to_send.append((dest_socket, response))
                    except Exception as e:
                        print(f"Error: {e}")
                        name = get_client_name(current_socket)
                        if name:
                            del clients[name]
                            print_names()
                        client_sockets.remove(current_socket)
                        current_socket.close()

            for message in messages_to_send:
                current_socket, data = message
                if current_socket in ready_to_write:
                    try:
                        current_socket.send(data.encode())  # Send response to the client
                        messages_to_send.remove(message)
                    except Exception as e:
                        print(f"Error sending message: {e}")
                        messages_to_send.remove(message)
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        for sock in client_sockets:
            sock.close()  # Close all client sockets
        server_socket.close()  # Close the server socket


if __name__ == '__main__':
    main()  # Start the server
