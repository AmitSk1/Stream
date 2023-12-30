
"""
client
Amit Skarbin
"""
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
import protocol

class StreamingClient:
    """
    A client class for streaming video data to a server.
    """

    def __init__(self, host, port, resolution=(
            RESOLUTION_VERTICAL, RESOLUTION_HORIZONTAL), fps=FPS):
        """
        Initializes the StreamingClient with the server address,
         resolution, and fps.
        """
        self.host = host
        self.port = port
        self.resolution = resolution
        self.fps = fps
        self.running = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Initialize the camera capture
        self.camera = cv2.VideoCapture(CAPTURE_DEVICE_INDEX)
        self.username = None  # To store the username

    def connect_to_server(self):
        """Establishes the socket connection with the server."""
        self.client_socket.connect((self.host, self.port))
        print("client connection")

    def start_stream(self, username):
        """
        Starts the video stream to the server.
        """
        self.username = username
        self.running = True
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        stream_thread = threading.Thread(target=self.stream_video)
        stream_thread.start()

    def stop_stream(self):
        """Stops the video stream and releases resources."""
        self.running = False
        self.camera.release()  # Release the camera
        self.client_socket.close()


    def stream_video(self):
        while self.running:
            screen_np = self.capture_screen()
            cam_frame = self.capture_camera_frame()
            if cam_frame is None:
                break

            combined_frame = self.combine_frames(screen_np, cam_frame)
            if not self.send_frame(combined_frame):
                break

        self.stop_stream()

    def capture_screen(self):
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
        # Resize screen capture
        return cv2.resize(screen_np, self.resolution)

    def capture_camera_frame(self):
        ret, cam_frame = self.camera.read()
        if not ret:
            print("Failed to grab frame from camera. Exiting...")
            return None
        return cv2.resize(cam_frame, self.resolution)

    def combine_frames(self, screen_np, cam_frame):
        return np.hstack((cam_frame, screen_np))

    def send_frame(self, frame):
        result, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_COMPRESSION_QUALITY])
        if not result:
            return False

        frame_and_username = (encoded_frame, self.username)
        data = pickle.dumps(frame_and_username, protocol=PICKLE_PROTOCOL_VERSION)

        try:
            protocol.send_bin(self.client_socket, data)
            return True
        except Exception as e:
            print(f"Connection closed: {e}")
            return False


    def stop_client(self):
        """
        Signals the client to stop streaming and shuts down the connection.
        """
        if self.running:
            print("Stopping the client...")
            self.stop_stream()  # Stop the streaming thread
            print("Client stopped.")
        else:
            print("Client is not running.")
