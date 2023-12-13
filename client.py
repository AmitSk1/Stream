
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
from CONSTANTS.constants import (
    FPS, RESOLUTION_VERTICAL, RESOLUTION_HORIZONTAL, CAPTURE_DEVICE_INDEX,
    JPEG_COMPRESSION_QUALITY, PICKLE_PROTOCOL_VERSION, WAIT_TIME_PER_FRAME
)


class StreamingClient:
    """
    A client for streaming video data to a server.
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
        """
        Captures video frames and sends them to the server.
        """
        while self.running:
            # Capture screen
            screen = pyautogui.screenshot()
            screen_np = np.array(screen)
            screen_np = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
            # Resize screen capture
            screen_np = cv2.resize(screen_np, self.resolution)

            # Capture camera frame
            ret, cam_frame = self.camera.read()
            if not ret:
                print("Failed to grab frame from camera. Exiting...")
                break
            # Resize camera capture
            cam_frame = cv2.resize(cam_frame, self.resolution)

            # Combine screen capture and camera frame side by side
            combined_frame = np.hstack((cam_frame, screen_np))

            # Compress the combined frame before sending
            result, encoded_frame = cv2.imencode('.jpg', combined_frame,
                                                 [cv2.IMWRITE_JPEG_QUALITY,
                                                  JPEG_COMPRESSION_QUALITY])
            data = pickle.dumps(encoded_frame,
                                protocol=PICKLE_PROTOCOL_VERSION)
            size = len(data)

            try:
                # Send username with the frame
                self.client_socket.sendall(struct.pack('>L', size) +
                                           data + self.username.encode())
            except Exception as e:
                print(f"Connection closed: {e}")
                break
            # Control the frame rate based on FPS
            cv2.waitKey(WAIT_TIME_PER_FRAME)

        self.stop_stream()

    def stop_client(self):
        """
        Signals the client to stop streaming and shuts down the connection.
        """
        if self.running:
            print("Stopping the client...")
            self.stop_stream()  # Stop the streaming thread
            # Additional cleanup if necessary
            print("Client stopped.")
        else:
            print("Client is not running.")