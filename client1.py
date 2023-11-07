import cv2
import socket
import struct
import pickle
import threading
import numpy as np
import pyautogui
from tkinter import Tk, Label, Button, Entry, StringVar


class StreamingClient:
    def __init__(self, host, port, resolution=(640, 360), fps=15):
        self.host = host
        self.port = port
        self.resolution = resolution
        self.fps = fps
        self.running = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera = cv2.VideoCapture(0)  # Initialize the camera capture
        self.username = None  # To store the username

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to server successfully.")
        except Exception as e:
            print(f"Failed to connect to server: {e}")

    def start_stream(self, username):
        self.username = username
        self.running = True
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        stream_thread = threading.Thread(target=self.stream_video)
        stream_thread.start()

    def stop_stream(self):
        self.running = False
        self.camera.release()  # Release the camera
        self.client_socket.close()

    def stream_video(self):
        while self.running:
            # Capture screen
            screen = pyautogui.screenshot()
            screen_np = np.array(screen)
            screen_np = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
            screen_np = cv2.resize(screen_np, self.resolution)  # Resize screen capture

            # Capture camera frame
            ret, cam_frame = self.camera.read()
            if not ret:
                print("Failed to grab frame from camera. Exiting...")
                break

            cam_frame = cv2.resize(cam_frame, self.resolution)  # Resize camera capture

            # Combine screen capture and camera frame side by side
            combined_frame = np.hstack((cam_frame, screen_np))

            # Compress the combined frame before sending
            result, encoded_frame = cv2.imencode('.jpg', combined_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            data = pickle.dumps(encoded_frame, protocol=4)
            size = len(data)

            try:
                # Send username with the frame
                self.client_socket.sendall(struct.pack('>L', size) + data + self.username.encode())
            except Exception as e:
                print(f"Connection closed: {e}")
                break

            cv2.waitKey(int(1000 / self.fps))  # Control the frame rate based on FPS

        self.stop_stream()
