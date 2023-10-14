"""
amit skarbin
"""
from vidstream import CameraClient, VideoClient, ScreenShareClient
import logging

logging.basicConfig(level=logging.INFO)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        pass

    def start_stream(self):
        pass

    def stop_stream(self):
        pass


class CameraStreamClient(Client):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.client = CameraClient(self.host, self.port)

    def start_stream(self):
        self.client.start_stream()
        logging.info("Started camera stream")

    def stop_stream(self):
        self.client.stop_stream()
        logging.info("Stopped camera stream")


class VideoStreamClient(Client):
    def __init__(self, host, port, video_file):
        super().__init__(host, port)
        self.client = VideoClient(self.host, self.port, video_file)

    def connect(self):
        self.client.connect()
        logging.info(f"Connected to server: {self.host}:{self.port}")

    def start_stream(self):
        self.client.start_stream()
        logging.info("Started video stream")

    def stop_stream(self):
        self.client.stop_stream()
        logging.info("Stopped video stream")


class ScreenShareStreamClient(Client):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.client = ScreenShareClient(self.host, self.port)

    def connect(self):
        self.client.connect()
        logging.info(f"Connected to server: {self.host}:{self.port}")

    def start_stream(self):
        self.client.start_stream()
        logging.info("Started screen share stream")

    def stop_stream(self):
        self.client.stop_stream()
        logging.info("Stopped screen share stream")


if __name__ == '__main__':
    client1 = CameraStreamClient('192.168.68.124', 4532)
    client2 = VideoStreamClient('192.168.68.124', 4532, 'video.mp4')
    client3 = ScreenShareStreamClient('192.168.68.124', 4532)

    client1.start_stream()

    client2.start_stream()

    client3.start_stream()
