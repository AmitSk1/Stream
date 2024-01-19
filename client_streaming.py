import cv2
import numpy as np
import pyautogui
from constants import RESOLUTION_VERTICAL, RESOLUTION_HORIZONTAL, CAPTURE_DEVICE_INDEX, JPEG_COMPRESSION_QUALITY, PICKLE_PROTOCOL_VERSION
import protocol

class ClientStreamingModule:
    def __init__(self, resolution=(RESOLUTION_VERTICAL, RESOLUTION_HORIZONTAL)):
        self.resolution = resolution
        self.camera = cv2.VideoCapture(CAPTURE_DEVICE_INDEX)

    def capture_screen(self):
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_BGR2RGB)
        return cv2.resize(screen_np, self.resolution)

    def capture_camera_frame(self):
        ret, cam_frame = self.camera.read()
        if not ret:
            print("Failed to grab frame from camera. Exiting...")
            return None
        return cv2.resize(cam_frame, self.resolution)

    def combine_frames(self, screen_np, cam_frame):
        return np.hstack((cam_frame, screen_np))

    # Additional streaming-related methods can be added here as needed
