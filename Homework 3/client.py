import socket
import select
import msvcrt
import sys
import protocol


# NAME <name> will set name. Server will reply error if duplicate
# GET_NAMES will get all names
# MSG <NAME> <message> will send message to client name
# EXIT will close client


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 7777))
    print("Enter commands\n")

    print("You: ", end="", flush=True)
    user_input = ""

    while True:
        # Use select to wait for either socket or keyboard input
        readable, _, _ = select.select([client_socket], [], [], 0.1)
        if client_socket in readable:
            try:
                msg = client_socket.recv(1024).decode().strip()
                if not msg:
                    break
                print("\r" + msg + "\nYou: " + user_input, end="", flush=True)
            except ConnectionResetError:
                break
        try:

            if msvcrt.kbhit():
                char = msvcrt.getch().decode('utf-8')  #
                if char == '\r':  # Enter key
                    if user_input == "EXIT":
                        client_socket.sendall("EXIT\n".encode())
                        break
                    client_socket.sendall(f"{user_input}\n".encode())
                    user_input = ""
                    print("\nYou: ", end="", flush=True)
                elif char == '\b':  # Backspace key
                    if user_input:
                        user_input = user_input[:-1]
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                elif not char.isalpha() and not char == " " and not char == "_":
                    print("ERROR\n")
                else:
                    user_input += char
                    sys.stdout.write(char)
                    sys.stdout.flush()
        except ConnectionResetError:
            break

    client_socket.close()


if __name__ == "__main__":
    main()
