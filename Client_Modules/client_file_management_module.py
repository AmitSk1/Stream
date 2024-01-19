import os

from Protocols import file_protocol, protocol


class ClientFileManagementModule:
    def __init__(self, file_socket):
        self.file_socket = file_socket

    def request_last_file(self):
        try:
            protocol.send(self.file_socket, "REQUEST_LAST_FILE")
        except Exception as e:
            print(f"Error requesting file: {e}")

    def receive_file_from_server(self, directory):
        file_protocol.recv_file(self.file_socket, directory)

    def upload_file(self, file_path, username):
        """Uploads a selected file to the server."""
        try:
            directory, base_name = os.path.split(file_path)
            new_file_name = os.path.join(directory, username + base_name)
            os.rename(file_path, new_file_name)
            protocol.send(self.file_socket, "UPLOAD_FILE")
            file_protocol.send_file(self.file_socket, new_file_name)
        except Exception as e:
            print(f"Error uploading file: {e}")

