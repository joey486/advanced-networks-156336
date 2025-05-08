"""Encrypted sockets implementation
   Author: Joesf Heiftez
   Date: 08/07/2024
"""

import random

LENGTH_FIELD_SIZE = 2
PORT = 8820

DIFFIE_HELLMAN_P = 39967  # big prime number
DIFFIE_HELLMAN_G = 39961

RSA_P = 137
RSA_Q = 151
RSA_PUBLIC_KEY = 2731
SIGNATURE_LENGTH = 5


def symmetric_encryption(input_data, key):
    """
    Return the encrypted/decrypted data.
    The key is 16 bits. If the length of the input data is odd, use only the bottom 8 bits of the key.
    Use XOR method.
    """
    # Ensure key is 16 bits
    if key < 0 or key > 0xFFFF:
        raise ValueError("Key must be a 16-bit integer")

    # Convert input_data to a bytearray if it is not already
    if isinstance(input_data, str):
        input_data = input_data.encode()
    input_data = bytearray(input_data)

    if len(input_data) % 2 != 0:
        key = key & 0xFF  # Use only the bottom 8 bits of the key

    # Perform the XOR operation
    for i in range(len(input_data)):
        input_data[i] ^= key

    return bytes(input_data)


def diffie_hellman_choose_private_key():
    """Choose a 16 bit size private key """
    return random.randint(0, 65535)


def diffie_hellman_calc_public_key(private_key):
    """G**private_key mod P"""
    return pow(DIFFIE_HELLMAN_G, private_key, DIFFIE_HELLMAN_P)


def diffie_hellman_calc_shared_secret(other_side_public, my_private):
    """other_side_public**my_private mod P"""
    return pow(other_side_public, my_private, DIFFIE_HELLMAN_P)


def calc_hash(message):
    """Create some sort of hash from the message
    Result must have a fixed size of 16 bits"""
    a = 64
    b = 24
    p = 131
    m = 37

    # Convert string message to an integer representation
    message_int = sum(ord(char) for char in message)

    return ((a * message_int + b) % p) % m & 0xFFFF


def calc_signature(hash_value, RSA_private_key):
    """Calculate the signature, using RSA algorithm
    hash**RSA_private_key mod (P*Q)"""
    return pow(hash_value, RSA_private_key, RSA_P * RSA_Q).to_bytes(SIGNATURE_LENGTH, byteorder='big')


def create_msg(data):
    """Create a valid protocol message, with length field
    For example, if data = "hello world",
    then "11hello world" should be returned"""
    length = len(data)
    length_bytes = str(length).encode()  # Convert the length to a byte string
    return length_bytes + data


def get_msg(my_socket):
    try:
        length_field = my_socket.recv(LENGTH_FIELD_SIZE)
        if not length_field:
            return False, "Error"
        length_field = length_field.decode()
        if not length_field.isdigit():
            return False, "Error"
        length = int(length_field)
        message = my_socket.recv(length)
        if not message:
            return False, "Error"
        message = message.decode()
        return True, message
    except (ConnectionAbortedError, ConnectionResetError) as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def Prime(num):  # prime function to check given number prime or not
    if num > 1:
        # Iterate from 2 to n // 2
        for i in range(2, (num // 2) + 1):
            # If num is divisible by any number between
            # 2 and n / 2, it is not prime
            if (num % i) == 0:
                return False
        else:
            return True
    else:
        return False


def check_RSA_public_key(totient):
    """Check that the selected public key satisfies the conditions
    key is prime
    key < totient
    totient mod key != 0"""
    return Prime(RSA_PUBLIC_KEY) and RSA_PUBLIC_KEY < totient and totient % RSA_PUBLIC_KEY != 0


def get_RSA_private_key(p, q, public_key):
    """Calculate the pair of the RSA public key.
    Use the condition: Private*Public mod Totient == 1
    Totient = (p-1)(q-1)"""
    totient = (p - 1) * (q - 1)
    for private_key in range(1, totient):
        if (private_key * public_key) % totient == 1:
            return private_key
    return None
