def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode().strip()
            if not msg:
                break
            print("\r" + msg + "\nYou: ", end="", flush=True)
        except ConnectionResetError:
            break
