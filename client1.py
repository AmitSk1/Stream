import cv2
import socket
import struct
import pickle
import threading
import numpy as np
import pyautogui
from constants import (
    FPS, RESOLUTION_VERTICAL, RESOLUTION_HORIZONTAL, CAPTURE_DEVICE_INDEX,
    JPEG_COMPRESSION_QUALITY, PICKLE_PROTOCOL_VERSION, WAIT_TIME_PER_FRAME
)


class StreamingClient:
    def __init__(self, host, port, resolution=(
            RESOLUTION_VERTICAL, RESOLUTION_HORIZONTAL), fps=FPS):
        self.host = host
        self.port = port
        self.resolution = resolution
        self.fps = fps
        self.running = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera = cv2.VideoCapture(CAPTURE_DEVICE_INDEX)
        self.username = None

    def connect_to_server(self):
        self.client_socket.connect((self.host, self.port))

    def start_stream(self, username):
        self.username = username
        self.running = True
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        stream_thread = threading.Thread(target=self.stream_video)
        stream_thread.start()

    def stop_stream(self):
        self.running = False
        self.camera.release()
        self.client_socket.close()

    def stream_video(self):
        while self.running:
            screen = pyautogui.screenshot()
            screen_np = np.array(screen)
            screen_np = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
            screen_np = cv2.resize(screen_np, self.resolution)

            ret, cam_frame = self.camera.read()
            if not ret:
                print("Failed to grab frame from camera. Exiting...")
                break
            cam_frame = cv2.resize(cam_frame, self.resolution)

            combined_frame = np.hstack((cam_frame, screen_np))
            result, encoded_frame = cv2.imencode('.jpg', combined_frame,
                                                 [cv2.IMWRITE_JPEG_QUALITY, JPEG_COMPRESSION_QUALITY])
            data = pickle.dumps(encoded_frame, protocol=PICKLE_PROTOCOL_VERSION)

            username_encoded = self.username.encode()
            frame_packet = struct.pack('>L', len(data)) + data + struct.pack('>L',
                                                                             len(username_encoded)) + username_encoded

            try:
                self.client_socket.sendall(frame_packet)
            except Exception as e:
                print(f"Connection closed: {e}")
                break
            cv2.waitKey(WAIT_TIME_PER_FRAME)

    def stop_client(self):
        if self.running:
            print("Stopping the client...")
            self.stop_stream()
            print("Client stopped.")
        else:
            print("Client is not running.")
