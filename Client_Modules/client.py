import pickle
import threading
import cv2
from Client_Modules.client_network_module import ClientNetworkModule
from Client_Modules.client_streaming import ClientStreamingModule
from Client_Modules.client_file_management_module \
    import ClientFileManagementModule
from constants import JPEG_COMPRESSION_QUALITY, PICKLE_PROTOCOL_VERSION
from Protocols import protocol


class StreamingClient:
    """
    A class representing a streaming client that sends video data to a server.

    Attributes:
        network_module (ClientNetworkModule): Manages network communication.
        streaming_module (ClientStreamingModule): Handles video streaming.
        file_management_module (ClientFileManagementModule): Manages file
        operations.
        username (str): The username of the client.
        running (bool): Indicates whether the streaming is active.
    """

    def __init__(self, host, port):
        """
        Initializes the streaming client with the specified server address.

        Args:
            host (str): The server's hostname or IP address.
            port (int): The port number on which the server is listening.
        """
        self.network_module = ClientNetworkModule(host, port)
        self.streaming_module = ClientStreamingModule()
        self.file_management_module = ClientFileManagementModule(
            self.network_module.file_socket)
        self.username = None
        self.running = False

    def start_stream(self, username):
        """
        Starts the video streaming process.

        Args:
            username (str): The username to be associated with the streamed
            video.
        """
        self.username = username
        self.running = True
        self.network_module.connect_to_server()
        stream_thread = threading.Thread(target=self.stream_video)
        stream_thread.start()

    def stop_stream(self):
        """
        Stops the video streaming process and releases resources.
        """
        self.running = False
        self.streaming_module.camera.release()
        self.network_module.close_sockets()
        print("Streaming stopped")

    def stream_video(self):
        """
        Continuously captures and sends video frames to the server.
        """
        while self.running:
            screen_np = self.streaming_module.capture_screen()
            cam_frame = self.streaming_module.capture_camera_frame()
            if cam_frame is None:
                break

            combined_frame = self.streaming_module.\
                combine_frames(screen_np, cam_frame)
            if not self.send_frame(combined_frame):
                break
        self.stop_stream()

    def send_frame(self, frame):
        """
        Encodes and sends a video frame to the server.

        Args:
            frame (numpy.ndarray): The video frame to send.

        Returns:
            bool: True if the frame was sent successfully, False otherwise.
        """
        protocol.send(self.network_module.stream_socket, "STREAM")
        result, encoded_frame = cv2.\
            imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY,
                                     JPEG_COMPRESSION_QUALITY])
        if not result:
            return False

        frame_and_username = (encoded_frame, self.username)
        data = pickle.dumps(frame_and_username,
                            protocol=PICKLE_PROTOCOL_VERSION)
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
            # Stop the file thread
            self.file_management_module.file_socket.close()
            print("Client stopped.")
        else:
            print("Client is not running.")
