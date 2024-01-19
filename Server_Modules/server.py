import socket

from Protocols import file_protocol, protocol
from Server_Modules.server_network_module import ServerNetworkModule
from Server_Modules.server_file_management_module import ServerFileManagementModule
from Server_Modules.serve_frame_processing_module import ServerFrameProcessingModule


class StreamingServer:
    def __init__(self, host, port, new_frame_callback=None):
        self.network_module = ServerNetworkModule(host, port, self.client_handler)
        self.file_management_module = ServerFileManagementModule()
        self.frame_processing_module = ServerFrameProcessingModule(new_frame_callback)

    def start_server(self):
        self.network_module.start_server()

    def stop_server(self):
        self.network_module.stop_server()

    def client_handler(self, client_socket, client_address):
        """
        Handles communication with a connected client.

        Args:
            client_socket (socket.socket): Socket for the client connection.
            client_address (tuple): Address of the client.
        """
        while self.network_module.running:
            try:
                data = protocol.recv(client_socket)
                if data == "REQUEST_LAST_FILE":
                    self.send_stored_file(client_socket)
                elif data == "STREAM":
                    self.handle_client_communication(client_socket, client_address)
                elif data == "UPLOAD_FILE":
                    self.file_management_module.store_client_file(client_socket)
            except ConnectionError as e:
                self.handle_disconnection(client_socket, client_address, e)
                break
            except Exception as e:
                self.log_error(client_address, e)
                break
        self.cleanup_connection(client_socket, client_address)

    def handle_client_communication(self, client_socket, client_address):
        data = protocol.recv_bin(client_socket)
        self.frame_processing_module.process_received_frame(data, client_address)

    def handle_disconnection(self, client_socket, client_address, error):
        del self.network_module.clients[client_address]  # Remove client from the dictionary when disconnected
        print(f"Client {client_address} disconnected: {error}")
        if self.frame_processing_module.new_frame_callback is not None:
            self.frame_processing_module.new_frame_callback(client_address, None, None)
        client_socket.close()

    def log_error(self, client_address, error):
        print(f"Error handling client {client_address}: {error}")
        if self.frame_processing_module.new_frame_callback is not None:
            self.frame_processing_module.new_frame_callback(client_address, None, None)

    def cleanup_connection(self, client_socket, client_address):
        client_socket.close()
        if self.frame_processing_module.new_frame_callback is not None:
            self.frame_processing_module.new_frame_callback(client_address, None, None)

    def send_stored_file(self, client_socket):
        if self.file_management_module.last_uploaded_file:
            file_protocol.send_file(client_socket, self.file_management_module.last_uploaded_file)
        else:
            print("No file has been uploaded yet.")
