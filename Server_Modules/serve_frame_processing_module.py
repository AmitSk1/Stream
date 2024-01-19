import pickle
import cv2
from constants import FRAME_DECODE_COLOR_MODE


class ServerFrameProcessingModule:
    def __init__(self, new_frame_callback=None):
        self.new_frame_callback = new_frame_callback

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
