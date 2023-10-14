from vidstream import StreamingServer
import threading
import logging

logging.basicConfig(level=logging.INFO)

class Server:
    def __init__(self, host, port):
        self.server = StreamingServer(host, port)
        self.clients = []
        self.lock = threading.Lock()

    def start_server(self):
        self.server.start_server()

    def add_client(self, client):
        with self.lock:
            self.clients.append(client)
            logging.info(f"New client connected: {client}")

    def remove_client(self, client):
        with self.lock:
            self.clients.remove(client)
            logging.info(f"Client disconnected: {client}")

    def broadcast(self, message):
        with self.lock:
            for client in self.clients:
                client.send(message)

if __name__ == '__main__':
    server = Server('192.168.68.120', 4532)
    server_thread = threading.Thread(target=server.start_server)
    server_thread.start()
