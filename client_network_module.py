import socket
import protocol

class ClientNetworkModule:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        """Establishes the socket connection with the server."""
        # self.client_socket.connect((self.host, self.port))
        self.file_socket.connect((self.host, self.port))
        self.stream_socket.connect((self.host, self.port))
        print("client connection")

    def close_sockets(self):
        self.file_socket.close()
        self.stream_socket.close()
        print("Sockets closed")

    # Additional network-related methods can be added here as needed
