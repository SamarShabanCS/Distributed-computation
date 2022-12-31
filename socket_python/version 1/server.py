'''
Auther Samar Abdelghani Haytamy
'''
import socket
import random
import sys
from threading import Thread
import os
import shutil
from pathlib import Path
import string

def get_working_directory_info(working_directory):
    """
    Creates a string representation of a working directory and its contents.
    :param working_directory: path to the directory
    :return: string of the directory and its contents.
    """
    dirs = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_dir()])
    files = '\n-- ' + '\n-- '.join([i.name for i in Path(working_directory).iterdir() if i.is_file()])
    dir_info = f'Current Directory: {working_directory}:\n|{dirs}{files}'
    return dir_info


def generate_random_eof_token():

    """Helper method to generates a random token that starts with '<' and ends with '>'.
     The total length of the token (including '<' and '>') should be 10.
     Examples: '<1f56xc5d>', '<KfOVnVMV>'
     return: the generated token.
     """
    #raise NotImplementedError('Your implementation here.')

    return '<'+''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))+'>'


def receive_message_ending_with_token(active_socket, buffer_size, eof_token):
    """
    Same implementation as in receive_message_ending_with_token() in client.py
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
    return message


def handle_cd(current_working_directory, new_working_directory):
    """
    Handles the client cd commands. Reads the client command and changes the current_working_directory variable 
    accordingly. Returns the absolute path of the new current working directory.
    :param current_working_directory: string of current working directory
    :param new_working_directory: name of the sub directory or '..' for parent
    :return: absolute path of new current working directory
    """
    try:
        os.chdir(new_working_directory)
    except OSError as e:
        print(f"something gets wrong when changing the directory, Exception:{e.strerror}, {sys.exc_info()} ")

    return os.getcwd()


def handle_mkdir(current_working_directory, directory_name):
    """
    Handles the client mkdir commands. Creates a new sub directory with the given name in the current working directory.
    :param current_working_directory: string of current working directory
    :param directory_name: name of new sub directory
    """
    try:
        final_directory = os.path.join(current_working_directory, directory_name)
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)
    # raise NotImplementedError('Your implementation here.')
    except OSError as e:
        print(f"something gets wrong when making directory, Exception: {e.strerror}, {sys.exc_info()} ")


def handle_rm(current_working_directory, object_name):
    """
    Handles the client rm commands. Removes the given file or sub directory. Uses the appropriate removal method
    based on the object type (directory/file).
    :param current_working_directory: string of current working directory
    :param object_name: name of sub directory or file to remove
    """
    try:
        if os.path.isfile(object_name):
            os.remove(object_name)
        elif os.path.isdir(object_name):
            os.rmdir(object_name)
        else:
            print(f"file  {object_name} doesn't exist")

    except OSError as e:
        print(f"something gets wrong when removing\n Error {e.filename}  - {e.strerror} ")


def handle_ul(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client ul commands. First, it reads the payload, i.e. file content from the client, then creates the
    file in the current working directory.
    Use the helper method: receive_message_ending_with_token() to receive the message from the client.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be created.
    :param service_socket: active socket with the client to read the payload/contents from.
    :param eof_token: a token to indicate the end of the message.
    """
    try:
        file_content = receive_message_ending_with_token(service_socket, 1024, eof_token)
        f = open(file_name, 'wb')
        f.write(file_content)
        f.close()
    except OSError as e:
        print(f"something gets wrong when uploading {file_name} \n Error {e.filename}  - {e.strerror} ")


def handle_dl(current_working_directory, file_name, service_socket, eof_token):
    """
    Handles the client dl commands. First, it loads the given file as binary, then sends it to the client via the
    given socket.
    :param current_working_directory: string of current working directory
    :param file_name: name of the file to be sent to client
    :param service_socket: active service socket with the client
    :param eof_token: a token to indicate the end of the message.
    """
    try:
        with open(file_name, 'rb') as f:
            file_content = f.read()

        file_content_with_token = file_content + eof_token.encode()
        # f.close()
        service_socket.sendall(file_content_with_token)
        print(f"the file: {file_name} was sent")
    except OSError as e:
        print(f"something gets wrong when downloading \n Error {e.filename}  - {e.strerror}, {sys.exc_info()} ")
        service_socket.sendall(b"error"+eof_token.encode())



class ClientThread(Thread):
    def __init__(self, service_socket: socket.socket, address: str):
        Thread.__init__(self)
        self.service_socket = service_socket
        self.address = address

    def run(self):
        # print ("Connection from : ", self.address)
        print("Connection from : ", self.address)
        # raise NotImplementedError('Your implementation here.')

        # initialize the connection
        # send random eof token
        eof_token = generate_random_eof_token()
        self.service_socket.send(str.encode(eof_token))

        # establish working directory
        current_directory = os.getcwd()
        cwd_info = get_working_directory_info(current_directory)+eof_token

        # send the current dir info
        self.service_socket.sendall(cwd_info.encode())
        print(f'Sent the cwd_info "{cwd_info}" to: {self.address}')
        while True:
            # get the command and arguments and call the corresponding method
            client_command = receive_message_ending_with_token(self.service_socket, 1024, eof_token)
            # client_command = self.service_socket.recv(1024)
            if not client_command:
                break
            d_client_command = client_command.decode().split()
            if d_client_command == "exit":
                exit(0)
            elif d_client_command[0] == "cd":
                current_directory = handle_cd(current_directory, d_client_command[1])
            elif d_client_command[0] == 'mkdir':
                handle_mkdir(current_directory, d_client_command[1])
            elif d_client_command[0] == 'dl':
                handle_dl(current_directory, d_client_command[1], self.service_socket, eof_token)
            elif d_client_command[0] == 'ul':
                print("will call ul handle \n ")
                handle_ul(current_directory, d_client_command[1], self.service_socket, eof_token)
            elif d_client_command[0] == 'rm':
                handle_rm(current_directory, d_client_command[1])
            else:
                print(f'incorrect command syntax')

            # send current dir info
            cwd_info = get_working_directory_info(os.getcwd())+eof_token
            self.service_socket.sendall(cwd_info.encode())

        # print('Connection closed from:', self.address)
        print('Connection closed from:', self.address)
        self.service_socket.close()

def main():
    try:
        HOST = "127.0.0.1"
        PORT = 65432
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                client_thread = ClientThread(conn, addr)
                client_thread.start()
                client_thread.join()
    except OSError as e:
        print(f"Error details:{e.strerror}, {sys.exc_info()} ")

if __name__ == '__main__':
    main()


