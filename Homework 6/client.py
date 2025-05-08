"""Encrypted socket client implementation
   Author: Joesf Heiftez
   Date: 08/07/2024
"""

import socket
import protocol


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(("127.0.0.1", protocol.PORT))

    # Diffie Hellman
    # 1 - choose private key
    private_diffie_key = protocol.diffie_hellman_choose_private_key()
    # 2 - calc public key
    public_diffie_key = protocol.diffie_hellman_calc_public_key(private_diffie_key)
    # 3 - interact with server and calc shared secret
    my_socket.send(str(public_diffie_key).encode())
    response = my_socket.recv(protocol.LENGTH_FIELD_SIZE).decode()  # wait for server response
    shared_secret = protocol.diffie_hellman_calc_shared_secret(int(response), private_diffie_key)

    # RSA
    private_RSA_key = 11669
    public_RSA_key = 1229

    while True:
        user_input = input("Enter command\n")
        if user_input == 'EXIT':
            break

        # Add MAC (signature)
        # 1 - calc hash of user input
        hash_value = protocol.calc_hash(user_input)
        # 2 - calc the signature
        signature = protocol.calc_signature(hash_value, private_RSA_key)

        # Encrypt
        encrypted_message = protocol.symmetric_encryption(user_input, shared_secret)

        # Send to server
        msg = protocol.create_msg(encrypted_message + signature)
        my_socket.send(msg)

        # Receive server's message
        valid_msg, message = protocol.get_msg(my_socket)
        if not valid_msg:
            print("Something went wrong with the length field")
            continue

        message = message.encode('utf-8')

        # Check if server's message is authentic
        encrypted_message, received_signature = message[:-5], int.from_bytes(message[-5:], byteorder='big')
        decrypted_message = protocol.symmetric_encryption(encrypted_message, shared_secret)
        received_hash = protocol.calc_hash(decrypted_message)
        calculated_hash = pow(received_signature, public_RSA_key, protocol.RSA_P * protocol.RSA_Q)

        if received_hash == calculated_hash:
            print(f"Server's message: {decrypted_message}")
        else:
            print("Authentication failed")

    print("Closing\n")
    my_socket.close()


if __name__ == "__main__":
    main()
