'''
Auther Samar Abdelghani Haytamy
'''
import socket
import sys


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in server.py
    A helper method to receives a bytearray message of arbitrary size sent on the socket.
    This method returns the message WITHOUT the eof_token at the end of the last packet.
    :param active_socket: a socket object that is connected to the server
    :param buffer_size: the buffer size of each recv() call
    :param eof_token: a token that denotes the end of the message.
    :return: a bytearray message with the eof_token stripped from the end.
    """

    message = bytearray()
    while True:
        packet = active_socket.recv(buffer_size)
        if packet[-10:] == eof_token.encode():
            message += packet[:-10]
            break
        message += packet
    # raise NotImplementedError('Your implementation here.')
    print(f'Got the file ')
    return message


def initialize(host, port):
    """
    1) Creates a socket object and connects to the server.
    2) receives the random token (10 bytes) used to indicate end of messages.
    3) Displays the current working directory returned from the server (output of get_working_directory_info() at the server).
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param host: the ip address of the server
    :param port: the port number of the server
    :return: the created socket object
    """

    # print('Connected to server at IP:', host, 'and Port:', port)
    print('Connected to server at IP:', host, 'and Port:', port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    eof_token = s.recv(10)
    d_eof_token = eof_token.decode()
    print(f"Handshake Done. EOF is:{d_eof_token}")
    msg_cwd_info = receive_message_ending_with_token(s, 1024, d_eof_token)
    print(f"Current working directory is:{msg_cwd_info.decode()}")
    return s, d_eof_token


def issue_cd(command_and_arg, client_socket, eof_token):
    """
    Sends the full cd command entered by the user to the server. The server changes its cwd accordingly and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    commnad_with_token = command_and_arg+eof_token
    client_socket.sendall(commnad_with_token.encode())
    cwd_info = receive_message_ending_with_token(client_socket, 1024, eof_token)
    print(cwd_info.decode())
    # raise NotImplementedError('Your implementation here.')


def issue_mkdir(command_and_arg, client_socket, eof_token):
    """
    Sends the full mkdir command entered by the user to the server. The server creates the sub directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    commnad_with_token = command_and_arg + eof_token
    print(f"I will sent {command_and_arg} command was sent")
    client_socket.sendall(str.encode(commnad_with_token))
    print("command was sent")
    cwd_info = receive_message_ending_with_token(client_socket, 1024, eof_token)
    print(cwd_info.decode())
    # raise NotImplementedError('Your implementation here.')


def issue_rm(command_and_arg, client_socket, eof_token):
    """
    Sends the full rm command entered by the user to the server. The server removes the file or directory and sends back
    the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    commnad_with_token = command_and_arg + eof_token
    client_socket.sendall(commnad_with_token.encode())
    cwd_info = receive_message_ending_with_token(client_socket, 1024, eof_token)
    print(cwd_info.decode())
    # raise NotImplementedError('Your implementation here.')


def issue_ul(command_and_arg, client_socket, eof_token):
    """
    Sends the full ul command entered by the user to the server. Then, it reads the file to be uploaded as binary
    and sends it to the server. The server creates the file on its end and sends back the new cwd info.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    """
    commnad_with_token = command_and_arg + eof_token
    try:
        file_name = command_and_arg.split()[1]
        client_socket.sendall(commnad_with_token.encode())
        f = open(file_name, 'rb')
        file_content = f.read()
        f.close()
        file_content_with_token = file_content+eof_token.encode()
        client_socket.sendall(file_content_with_token)
    except OSError as e:
        print(f"Error while uploading{file_name}, error: {e.strerror}, {sys.exc_info()} ")

    cwd_info = receive_message_ending_with_token(client_socket, 1024, eof_token)
    print(cwd_info.decode())
    # raise NotImplementedError('Your implementation here.')


def issue_dl(command_and_arg, client_socket, eof_token):
    """
    Sends the full dl command entered by the user to the server. Then, it receives the content of the file via the
    socket and re-creates the file in the local directory of the client. Finally, it receives the latest cwd info from
    the server.
    Use the helper method: receive_message_ending_with_token() to receive the message from the server.
    :param command_and_arg: full command (with argument) provided by the user.
    :param client_socket: the active client socket object.
    :param eof_token: a token to indicate the end of the message.
    :return:
    """
    try:
        commnad_with_token = command_and_arg + eof_token
        client_socket.sendall(commnad_with_token.encode())
        file_name = command_and_arg.split()[1]
        file_content = receive_message_ending_with_token(client_socket, 1024, eof_token)  # download file
        if file_content.decode() == "error":
            print('Exception in the server, Error')
        else:
            with open(file_name, 'wb') as f:
                f.write(file_content)
            f.close()
            print(f'the file {file_name} was written')
            cwd_info = receive_message_ending_with_token(client_socket, 1024, eof_token)
            print(cwd_info.decode())
    except:
        print(f'Exception in the client,{ sys.exc_info()}')



    # raise NotImplementedError('Your implementation here.')


def main():
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

 #   raise NotImplementedError('Your implementation here.')

    # initialize
    active_soc, eof_token = initialize(HOST, PORT)
    print(f" the socket: {active_soc}")

    while True:
        # get user input
        command_args = input(f"enter your command example (cd x /cd .. @ mkdir x2 @ rm x2 @ ul pic.jpg @ dl pic.jpg @ exit)")
        # call the corresponding command function or exit
        if command_args == "exit":
            exit(0)
        elif "cd " in command_args:
            issue_cd(command_args, active_soc, eof_token)
        elif 'mkdir ' in command_args:
            issue_mkdir(command_args, active_soc, eof_token)
        elif 'dl ' in command_args:
            issue_dl(command_args, active_soc, eof_token)
        elif 'ul ' in command_args:
            issue_ul(command_args, active_soc, eof_token)
        elif 'rm ' in command_args:
            issue_rm(command_args, active_soc, eof_token)
        else:
            print(f'Not recognized command')

    print('Exiting the application.')


if __name__ == '__main__':
    main()
