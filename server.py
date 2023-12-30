import socket
import threading
import struct
import pickle
import cv2

import protocol
from constants import (
    PAYLOAD_SIZE_STRUCT_FORMAT, RECEIVE_BUFFER_SIZE,
    FRAME_DECODE_COLOR_MODE
)


class StreamingServer:
    """
    A server class for handling video streaming from multiple clients.

    Attributes:
        host (str): Host address of the server.
        port (int): Port number the server listens on.
        server_socket (socket.socket): Socket for the server.
        new_frame_callback (function): Callback function that is
        called when a new frame is received.
        running (bool): Flag indicating whether the server is running.
    """

    def __init__(self, host, port, new_frame_callback=None):
        """
        Initializes the streaming server with host and port.
        :param host:
        :param port:
        :param new_frame_callback:
        """
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.new_frame_callback = new_frame_callback
        self.running = False

    def start_server(self):
        """
        Starts the server to listen for incoming connections and handle them.
        """
        self.server_socket.listen()
        self.running = True
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.start()

    def accept_connections(self):
        """
        Accepts incoming connections and starts a new thread for each client.
        """
        while self.running:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.client_handler,
                                             args=(client_socket,
                                                   client_address))
            client_thread.start()

    def client_handler(self, client_socket, client_address):
        """
        Handles communication with a connected client.

        Args:
            client_socket (socket.socket): Socket for the client connection.
            client_address (tuple): Address of the client.
        """
        while self.running:
            try:
                self.handle_client_communication(client_socket, client_address)
            except ConnectionError as e:
                self.handle_disconnection(client_socket, client_address, e)
                break
            except Exception as e:
                self.log_error(client_address, e)
                break
        self.cleanup_connection(client_socket, client_address)

    def handle_client_communication(self, client_socket, client_address):
        data = protocol.recv_bin(client_socket)
        self.process_received_frame(data, client_address)

    def process_received_frame(self, data, client_address):
        # Process the received frame
        try:
            frame_data, username = pickle.loads(data)
            frame = cv2.imdecode(frame_data, FRAME_DECODE_COLOR_MODE)
            if frame is not None:
                # If a callback is set, invoke it with the frame and client info
                if self.new_frame_callback is not None:
                    self.new_frame_callback(client_address, frame, username)
        except Exception as e:
            print(f"Error decoding frame from client {client_address}: {e}")

    def handle_disconnection(self, client_socket, client_address, error):
        print(f"Client {client_address} disconnected: {error}")
        if self.new_frame_callback is not None:
            self.new_frame_callback(client_address, None, None)
        client_socket.close()

    def log_error(self, client_address, error):
        print(f"Error handling client {client_address}: {error}")
        if self.new_frame_callback is not None:
            self.new_frame_callback(client_address, None, None)

    def cleanup_connection(self, client_socket, client_address):
        client_socket.close()
        if self.new_frame_callback is not None:
            self.new_frame_callback(client_address, None, None)

    def stop_server(self):
        """
         Stops the server and closes all resources.
         """
        self.running = False
        self.server_socket.close()
        cv2.destroyAllWindows()
