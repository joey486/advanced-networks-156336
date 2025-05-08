import socket
import SMTP_protocol
import base64

CLIENT_NAME = "client.net"

# Add the minimum required fields to the email
EMAIL_TEXT = \
    "From: <gurpartap@patriots.in>\r\n" \
    "RCPT TO: <raj_deol2002in@yahoo.co.in>\r\n" \
    "<p class=3DMsoNormal>Hello<o:p></o:p></p>\r\n" \
    "\r\n<p class=3DMsoNormal><o:p>&nbsp;</o:p></p>\r\n" \
    "\r\n<p class=3DMsoNormal>I send u smtp pcap file <o:p></o:p></p>\r\n" \
    "\r\n<p class=3DMsoNormal>Find the attachment<o:p></o:p></p>\r\n" \
    "\r\n<p class=3DMsoNormal><o:p>&nbsp;</o:p></p>\r\n" \
    "\r\n<p class=3DMsoNormal>GPS<o:p></o:p></p>\r\n" \
    "\r\n</div>\r\n\r\n</body>\r\n\r\n</html>\r\n\r\n------=_NextPart_001_0005_01CA45B0.095693F0--" \


def create_EHLO():
    return "EHLO {}\r\n".format(CLIENT_NAME).encode()


# More functions must follow, in the form of create_EHLO, for every client message
# ...

def main():
    # Connect to server
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket.AF_INET - IPV4, socket.SOCK_STREAM - TCP
    my_socket.connect(("127.0.0.1", 8820))

    # 1 server welcome message
    my_socket.send("SACK_PERM".encode())

    # Check that the welcome message is according to the protocol
    data = my_socket.recv(1024).decode()  # why 1024?
    print("" + data)    # ?

    # 2 EHLO message
    message = create_EHLO()
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("Error connecting")
        my_socket.close()
        return

    # 3 AUTH LOGIN
    message = "AUTH LOGIN"
    my_socket.send(message)

    response = my_socket.recv(1024).decode()
    print(response)

    # 4 User
    user = "barbie"

    response = my_socket.recv(1024).decode()
    print(response)

    # 5 password
    password = "helloken"
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    print(response)

    # 6 mail from
    message = "MAIL FROM"
    my_socket.send(message)

    # 7 rcpt to
    response = my_socket.recv(1024).decode()

    # 8 data
    response = my_socket.recv(1024).decode()

    # 9 email content
    response = my_socket.recv(1024).decode()

    # 10 quit
    message = "QUIT"
    my_socket.send(message)
    response = my_socket.recv(1024).decode()
    print("Closing\n")
    my_socket.close()


if __name__ == "__main__":
    main()
