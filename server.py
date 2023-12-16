import socket
import threading
import struct
import pickle
import cv2
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
        payload_size = struct.calcsize(PAYLOAD_SIZE_STRUCT_FORMAT)
        while self.running:
            try:
                # Receive the data from the client
                data = b""
                while len(data) < payload_size:
                    packet = client_socket.recv(RECEIVE_BUFFER_SIZE)
                    if not packet:  # Client has disconnected
                        raise ConnectionError("Client disconnected")
                    data += packet

                # Retrieve the size of the incoming frame data
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(PAYLOAD_SIZE_STRUCT_FORMAT,
                                         packed_msg_size)[0]

                # Receive the frame data based on the retrieved size
                while len(data) < msg_size:
                    data += client_socket.recv(RECEIVE_BUFFER_SIZE)

                frame_data = data[:msg_size]

                # Decoding the frame should be in a try-except block
                # to handle corrupt data
                try:
                    frame_data, username = pickle.loads(frame_data)
                    frame = cv2.imdecode(frame_data, FRAME_DECODE_COLOR_MODE)
                    if frame is not None:
                        # Use a thread-safe method to update the GUI
                        self.new_frame_callback(client_address,
                                                frame, username)
                except Exception as e:
                    print(f"Error decoding frame from client "
                          f"{client_address}: {e}")

            except ConnectionError as e:
                print(f"Client {client_address} disconnected: {e}")
                self.new_frame_callback(client_address, None, username)
                break
            except Exception as e:
                print(f"Error handling client {client_address}: {e}")
                self.new_frame_callback(client_address, None, username)
                break

        # Clean up the connection
        client_socket.close()
        # Notify the GUI that the client has disconnected
        if self.new_frame_callback:
            self.new_frame_callback(client_address, None, username)

    def stop_server(self):
        """
         Stops the server and closes all resources.
         """
        self.running = False
        self.server_socket.close()
        cv2.destroyAllWindows()
