import cv2
import numpy as np
import socket
import threading
import struct
import pickle

class StreamingServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.frames = {}
        self.lock = threading.Lock()
        self.running = False

    def start_server(self):
        self.server_socket.listen()
        self.running = True
        print(f"Server started at {self.host}:{self.port}")
        threading.Thread(target=self.accept_connections, daemon=True).start()
        self.update_combined_frame()

    def accept_connections(self):
        while self.running:
            client_socket, _ = self.server_socket.accept()
            threading.Thread(target=self.client_handler, args=(client_socket,)).start()

    def client_handler(self, client_socket):
        payload_size = struct.calcsize(">L")
        while self.running:
            data = b""
            while len(data) < payload_size:
                data += client_socket.recv(4096)
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            while len(data) < msg_size:
                data += client_socket.recv(4096)
            frame_data = data[:msg_size]
            frame = pickle.loads(frame_data)
            client_id = client_socket.getpeername()  # Using client's address as ID
            with self.lock:
                self.frames[client_id] = frame

    def update_combined_frame(self):
        while self.running:
            with self.lock:
                if self.frames:
                    combined_frame = self.combine_frames(list(self.frames.values()))
                    cv2.imshow('Server', combined_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.stop_server()

    def combine_frames(self, frames):
        num_frames = len(frames)
        grid_size = int(np.ceil(np.sqrt(num_frames)))
        frame_height, frame_width = frames[0].shape[:2]
        combined_frame = np.zeros((frame_height * grid_size, frame_width * grid_size, 3), dtype=np.uint8)
        for idx, frame in enumerate(frames):
            x = (idx % grid_size) * frame_width
            y = (idx // grid_size) * frame_height
            combined_frame[y:y+frame_height, x:x+frame_width, :] = frame
        return combined_frame

    def stop_server(self):
        self.running = False
        self.server_socket.close()
        cv2.destroyAllWindows()