"""Encrypted socket server implementation
   Author: Joesf Heiftez
   Date: 08/07/2024
"""

import socket
import protocol


def create_server_rsp(cmd):
    """Based on the command, create a proper response"""
    return f"Server response to: {cmd}"


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", protocol.PORT))
    server_socket.listen()
    print("Server is up and running")
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")

    # Diffie Hellman
    # 1 - choose private key
    private_diffie_key = protocol.diffie_hellman_choose_private_key()
    # 2 - calc public key
    public_diffie_key = protocol.diffie_hellman_calc_public_key(private_diffie_key)
    # 3 - interact with client and calc shared secret
    client_socket.send(str(public_diffie_key).encode())
    response = client_socket.recv(protocol.LENGTH_FIELD_SIZE).decode()  # wait for client response
    shared_secret = protocol.diffie_hellman_calc_shared_secret(int(response), private_diffie_key)

    # RSA
    private_RSA_key = 7171
    public_RSA_key = 2731

    while True:
        # Receive client's message
        valid_msg, message = protocol.get_msg(client_socket)
        if not valid_msg:
            print("Something went wrong with the length field")
            continue

        if message == "EXIT":
            break

        message = message.encode('utf-8')

        # Separate the message and the MAC
        encrypted_message, received_signature = message[:-5], int.from_bytes(message[-5:], byteorder='big')
        decrypted_message = protocol.symmetric_encryption(encrypted_message, shared_secret)
        received_hash = protocol.calc_hash(decrypted_message)
        calculated_hash = pow(received_signature, public_RSA_key, protocol.RSA_P * protocol.RSA_Q)

        if received_hash == calculated_hash:
            print(f"Client's message: {decrypted_message}")
            response = create_server_rsp(decrypted_message)
        else:
            print("Authentication failed")
            response = "Authentication failed"

        # Encrypt response
        response_hash = protocol.calc_hash(response)
        response_signature = protocol.calc_signature(response_hash, private_RSA_key)
        encrypted_response = protocol.symmetric_encryption(response, shared_secret)

        # Send to client
        msg = protocol.create_msg(encrypted_response + response_signature)
        client_socket.send(msg)

    print("Closing\n")
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()
