import pickle
import threading

import cv2
from client_network_module import ClientNetworkModule
from client_streaming import ClientStreamingModule
from ClientFileManagementModule import ClientFileManagementModule
from constants import JPEG_COMPRESSION_QUALITY, PICKLE_PROTOCOL_VERSION

import protocol


class StreamingClient:
    def __init__(self, host, port):
        self.network_module = ClientNetworkModule(host, port)
        self.streaming_module = ClientStreamingModule()
        self.file_management_module = ClientFileManagementModule(self.network_module.file_socket)
        self.username = None
        self.running = False

    def start_stream(self, username):
        self.username = username
        self.running = True
        self.network_module.connect_to_server()
        stream_thread = threading.Thread(target=self.stream_video)
        stream_thread.start()

    def stop_stream(self):
        self.running = False
        self.streaming_module.camera.release()
        self.network_module.close_sockets()
        print("Streaming stopped")

    def stream_video(self):
        while self.running:
            screen_np = self.streaming_module.capture_screen()
            cam_frame = self.streaming_module.capture_camera_frame()
            if cam_frame is None:
                break

            combined_frame = self.streaming_module.combine_frames(screen_np, cam_frame)
            if not self.send_frame(combined_frame):
                break
        self.stop_stream()

    def send_frame(self, frame):
        protocol.send(self.network_module.stream_socket, "STREAM")
        result, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_COMPRESSION_QUALITY])
        if not result:
            return False

        frame_and_username = (encoded_frame, self.username)
        data = pickle.dumps(frame_and_username, protocol=PICKLE_PROTOCOL_VERSION)
        try:
            protocol.send_bin(self.network_module.stream_socket, data)
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
            self.file_management_module.file_socket.close()  # stop the file thread
            print("Client stopped.")
        else:
            print("Client is not running.")