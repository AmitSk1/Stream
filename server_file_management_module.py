import os
import file_protocol

class ServerFileManagementModule:
    def __init__(self):
        self.last_uploaded_file = None

    def store_client_file(self, client_socket):
        directory = "C:/client_files"
        # Check if the directory exists, create it if not
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_protocol.recv_file(client_socket, directory)
        print("file stored successfully in" + directory)

    def send_stored_file(self, client_socket):
        if self.last_uploaded_file:
            file_protocol.send_file(client_socket, self.last_uploaded_file)
        else:
            print("No file has been uploaded yet.")


    def upload_file(self, file_path):
        self.last_uploaded_file = file_path
        print("Uploading file" + file_path)