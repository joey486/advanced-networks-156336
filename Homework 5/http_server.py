# Ex 4.4 - HTTP Server Shell
# Author: Barak Gonen
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files, or other utilities, for educational purposes
# Usage: Fill the missing functions and constants

# name: joey heifetz
# ID: 216175398

# Import modules
import socket
import os

# Set constants
IP = '0.0.0.0'  # Listen on all available network interfaces
PORT = 80  # Port to listen on
SOCKET_TIMEOUT = 0.1  # Timeout for socket operations in seconds
DEFAULT_URL = "index.html"  # Default file to serve if no specific resource is requested
REDIRECTION_DICTIONARY = {
    "js/box.js": "js/box1.js"
}  # Dictionary for handling URL redirections
ROOT_DIR = "webroot"  # Root directory for the web server files
FIXED_RESPONSE = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nHello"  # Placeholder response for initial connection


def get_file_data(filename):
    """ Get data from file """
    # Open the file in binary mode and read its contents
    with open(filename, 'rb') as file:
        return file.read()


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response, and send it to the client """
    # Determine the URL to serve based on the resource requested
    if resource.startswith('/calculate-next'):
        handle_calculate_next(resource, client_socket)
        return

    if resource.startswith('/calculate-area'):
        handle_calculate_area(resource, client_socket)
        return

    if resource == '/':
        url = DEFAULT_URL
    else:
        url = resource.lstrip('/')

    # Check if the URL has been redirected
    if url in REDIRECTION_DICTIONARY:
        # Send a 302 redirection response
        http_header = "HTTP/1.1 302 Found\r\nLocation: {}\r\n\r\n".format(REDIRECTION_DICTIONARY[url])
        print(http_header)
        client_socket.send(http_header.encode())
        return

    # Determine the file path to serve
    file_path = os.path.join(ROOT_DIR, url)
    if not os.path.isfile(file_path):
        # Send a 404 Not Found response if the file does not exist
        http_header = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
        client_socket.send(http_header.encode())
        return

    # Determine the file type based on the file extension
    filetype = url.split('.')[-1]
    if filetype == 'html':
        # Generate an HTTP header for HTML files
        http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
    elif filetype == 'jpg':
        # Generate an HTTP header for JPEG files
        http_header = "HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n"
    elif filetype == 'css':
        http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n"
    elif filetype == 'ico':
        http_header = "HTTP/1.1 200 OK\r\nContent-Type: image/x-icon\r\n\r\n"
    elif filetype == 'js':
        http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/javascript\r\n\r\n"
    else:
        # Generate a generic HTTP header for other file types
        http_header = "HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\n\r\n"

    # Read the data from the file
    data = get_file_data(file_path)
    # Combine the HTTP header and file data into a single response
    http_response = http_header.encode() + data
    # Send the HTTP response to the client
    client_socket.send(http_response)


def handle_calculate_next(resource, client_socket):
    query = resource.split('?')[-1]
    params = dict(param.split('=') for param in query.split('&'))
    num = int(params.get('num', 0))
    result = num + 1

    http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n"
    http_response = http_header + str(result)
    client_socket.send(http_response.encode())


def handle_calculate_area(resource, client_socket):
    query = resource.split('?')[-1]
    params = dict(param.split('=') for param in query.split('&'))
    height = int(params.get('height', 0))
    width = int(params.get('width', 0))

    result = height * width / 2

    http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n"
    http_response = http_header + str(result)
    client_socket.send(http_response.encode())


def validate_http_request(request):
    """
    Check if the request is a valid HTTP request and return TRUE / FALSE and the requested URL
    """
    # Split the request into parts
    parts = request.split(' ')
    # Check if the request is a valid HTTP GET request
    if len(parts) >= 3 and parts[0] == 'GET' and parts[2].startswith('HTTP/'):
        return True, parts[1]
    return False, None


def handle_client(client_socket):
    """ Handle client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    while True:
        try:
            # Receive the client's request
            client_request = client_socket.recv(1024).decode()
            if not client_request:
                # If no request is received, break the loop
                break
            # Validate the HTTP request
            valid_http, resource = validate_http_request(client_request)
            if valid_http:
                print('Got a valid HTTP request')
                # Handle the client request
                handle_client_request(resource, client_socket)
                break
            else:
                print('Error: Not a valid HTTP request')
                break
        except socket.timeout:
            break
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    try:
        while True:
            # Accept a new client connection
            client_socket, client_address = server_socket.accept()
            print('New connection received')
            # Set a timeout for the client socket
            client_socket.settimeout(SOCKET_TIMEOUT)
            # Handle the client connection
            handle_client(client_socket)
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()
