"""
Amit skarbin
"""

import os
import struct
from constants import CHUNK_SIZE


class FileProtocol:

    @staticmethod
    def send_file(sock, file_path):
        """
        Sends a file over a socket.

        Args:
            sock (socket.socket): The socket over which to send the file.
            file_path (str): The path of the file to send.
        """
        file_name = os.path.basename(file_path)
        file_name_encoded = file_name.encode()

        # Send the file name size and file name
        sock.sendall(struct.pack('>Q', len(file_name_encoded)))
        sock.sendall(file_name_encoded)

        # Send the file content
        with open(file_path, 'rb') as file:
            file_size = os.path.getsize(file_path)
            sock.sendall(struct.pack('>Q', file_size))

            while True:
                data = file.read(CHUNK_SIZE)
                if not data:
                    break
                sock.sendall(data)

    @staticmethod
    def recv_file(sock, directory):
        """
        Receives a file over a socket and saves it to the specified directory.

        Args:
            sock (socket.socket): The socket from which to receive the file.
            directory (str): The directory where the file will be saved.
        """
        # Receive the file name size and file name
        name_size_data = sock.recv(8)
        name_size = struct.unpack('>Q', name_size_data)[0]
        file_name_encoded = sock.recv(name_size)
        file_name = file_name_encoded.decode()

        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        save_path = os.path.join(directory, file_name)

        # Receive the file content
        file_size_data = sock.recv(8)
        file_size = struct.unpack('>Q', file_size_data)[0]

        with open(save_path, 'wb') as file:
            received_size = 0
            while received_size < file_size:
                data = sock.recv(min(CHUNK_SIZE, file_size - received_size))
                if not data:
                    break
                file.write(data)
                received_size += len(data)
