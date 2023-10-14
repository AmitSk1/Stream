from vidstream import CameraClient, ScreenShareClient
import logging

logging.basicConfig(level=logging.INFO)


class Client:
    def __init__(self, host, port, client_number):
        self.host = host
        self.port = port
        self.client_number = client_number
        self.client = None

    def start_stream(self):
        self.client = CameraClient(self.host, self.port)
        self.client.start_stream()
        self.client2 = ScreenShareClient(self.host, self.port)
        self.client2.start_stream()

        while True:
            frame1 = self.client.read()
            frame2 = self.client2.read()

            logging.info(f"Client {self.client_number} - Camera Frame: {frame1}")
            logging.info(f"Client {self.client_number} - Screen Frame: {frame2}")

    def stop_stream(self):
        self.client.stop_stream()
        self.client2.stop_stream()


if __name__ == '__main__':
    client1 = Client('192.168.68.124', 4532, 1)
    client1.start_stream()

    client2 = Client('192.168.68.124', 4532, 2)
    client2.start_stream()
