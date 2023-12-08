import socket
import threading
import struct
import pickle
import cv2
from constants import (
    PAYLOAD_SIZE_STRUCT_FORMAT, RECEIVE_BUFFER_SIZE,
    FRAME_DECODE_COLOR_MODE, KEY_PRESS_CHECK_DELAY, EXIT_KEY
)

class StreamingServer:
    def __init__(self, host, port, new_frame_callback=None):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.new_frame_callback = new_frame_callback
        self.running = False

    def start_server(self):
        self.server_socket.listen()
        self.running = True
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.start()

    def accept_connections(self):
        while self.running:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.client_handler, args=(client_socket, client_address))
            client_thread.start()

    def client_handler(self, client_socket, client_address):
        payload_size = struct.calcsize(PAYLOAD_SIZE_STRUCT_FORMAT)
        while self.running:
            try:
                data = b""
                while len(data) < payload_size:
                    packet = client_socket.recv(RECEIVE_BUFFER_SIZE)
                    if not packet:
                        break
                    data += packet

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(PAYLOAD_SIZE_STRUCT_FORMAT, packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(RECEIVE_BUFFER_SIZE)

                frame_data = data[:msg_size]
                frame = pickle.loads(frame_data)
                frame = cv2.imdecode(frame, FRAME_DECODE_COLOR_MODE)

                if self.new_frame_callback:
                    self.new_frame_callback(client_address, frame)

            except Exception as e:
                print(f"Error handling client: {e}")
                break

        client_socket.close()

    def stop_server(self):
        self.running = False
        self.server_socket.close()
        cv2.destroyAllWindows()
