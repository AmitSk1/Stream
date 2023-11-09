import socket
import threading
import struct
import pickle
import cv2


class StreamingServer:
    """
    A server for handling incoming video streams from multiple clients.

    """

    def __init__(self, host, port):
        """
        Initializes the StreamingServer with the server address.
        """
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.clients = {}
        self.client_info = {}  # To store the username for each client
        self.lock = threading.Lock()
        self.running = False

    def start_server(self):
        """Starts the server to listen for incoming connections."""
        self.server_socket.listen()
        self.running = True
        print(f"Server started at {self.host}:{self.port}")
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.start()

    def accept_connections(self):
        """Accepts incoming client connections and starts a handler for each."""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection from {client_address} has been established.")
                client_thread = threading.Thread(target=self.client_handler, args=(client_socket,))
                client_thread.start()
            except Exception as e:
                print(f"Error accepting connections: {e}")

    def client_handler(self, client_socket):
        """
        Handles the communication with a connected client.
        """
        payload_size = struct.calcsize('>L')
        while self.running:
            try:
                data = b""
                while len(data) < payload_size:
                    packet = client_socket.recv(4096)
                    if not packet: break
                    data += packet
                if data == b"": break

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(4096)

                # Frame data and username are being transmitted together, so we split them
                frame_data = data[:msg_size]
                username_data = data[msg_size:]
                data = b""

                # Extract username; assume that it's at the end of the transmission
                username = username_data.decode('utf-8').rstrip('\x00')

                frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                # Display the frame
                window_title = f"Stream - {username}"
                cv2.imshow(window_title, frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except ConnectionResetError:
                break

        client_socket.close()
        print(f"Client disconnected")

    def stop_server(self):
        """Stops the server and releases all resources."""
        self.running = False
        self.server_socket.close()
        cv2.destroyAllWindows()
        print("Server stopped.")
