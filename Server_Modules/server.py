"""
Server
Amit Skarbin
"""

import socket

from Protocols import file_protocol, protocol
from Server_Modules.server_network_module import ServerNetworkModule
from Server_Modules.server_file_management_module \
    import ServerFileManagementModule
from Server_Modules.serve_frame_processing_module \
    import ServerFrameProcessingModule


class StreamingServer:
    """
    A server class for handling video streaming from multiple clients.

    This class manages the server operations including network communication,
    file management, and frame processing.

    Attributes:
        network_module (ServerNetworkModule): Manages network communication.
        file_management_module (ServerFileManagementModule):
        Handles file operations.
        frame_processing_module (ServerFrameProcessingModule):
        Manages frame processing.
    """

    def __init__(self, host, port, new_frame_callback=None):
        """
        Initializes the StreamingServer with host, port, and frame callback.

        Args:
            host (str): Host address of the server.
            port (int): Port number the server listens on.
            new_frame_callback (function): Callback function for new frames.
        """
        self.network_module = ServerNetworkModule(host,
                                                  port, self.client_handler)
        self.file_management_module = ServerFileManagementModule()
        self.frame_processing_module = ServerFrameProcessingModule(
            new_frame_callback)

    def start_server(self):
        """
        Starts the server to listen for incoming connections.
        """
        self.network_module.start_server()

    def stop_server(self):
        """
        Stops the server and closes all resources.
        """
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
                    self.file_management_module.send_stored_file(client_socket)
                elif data == "STREAM":
                    self.handle_client_communication(client_socket,
                                                     client_address)
                elif data == "UPLOAD_FILE":
                    self.file_management_module. \
                        store_client_file(client_socket)
                elif data == "STOP":
                    self.handle_disconnection(client_socket, client_address,
                                              error="client closed")
            except ConnectionError as e:
                print("Connection error")
                self.handle_disconnection(client_socket, client_address, e)
                break
            except Exception as e:
                self.log_error(client_address, e)
                break
        self.cleanup_connection(client_socket, client_address)

    def handle_finish_test(self):
        self.network_module.notify_clients_test_over()

    def handle_client_communication(self, client_socket, client_address):
        data = protocol.recv_bin(client_socket)
        self.frame_processing_module. \
            process_received_frame(data, client_address)

    def diconnection(self, client_socket, client_address):
        # Remove client from the dictionary when disconnected
        print("Client disconnected")
        del self.network_module.clients[client_address]
        print(f"Client {client_address} disconnecte")
        if self.frame_processing_module.new_frame_callback is not None:
            self.frame_processing_module \
                .new_frame_callback(client_address, None, None)
        client_socket.close()

    def handle_disconnection(self, client_socket, client_address, error=None):
        """
        Handles the disconnection of a client, ensuring that resources are cleaned up and the system is updated.

        Args:
            client_socket (socket.socket): The socket associated with the disconnected client.
            client_address (tuple): The address of the disconnected client.
            error (str, optional): An optional error message indicating the reason for disconnection.
        """
        # Log the disconnection event, including any error messages if provided
        if error:
            print(
                f"Client {client_address} disconnected due to error: {error}")
        else:
            print(f"Client {client_address} disconnected gracefully.")

        # Remove the client from the server's list of active clients
        # This assumes that your server maintains a dictionary or similar structure of active clients
        if client_address in self.network_module.clients:
            del self.network_module.clients[client_address]
            print(f"Removed client {client_address} from active clients list.")

        # Perform any necessary cleanup of resources associated with the client
        # This could include closing the client's socket, releasing any locks, etc.
        try:
            client_socket.close()
            print(f"Closed socket for client {client_address}.")
        except Exception as e:
            print(f"Error closing socket for client {client_address}: {e}")

        if self.frame_processing_module.new_frame_callback is not None:
            self.frame_processing_module.new_frame_callback(client_address,
                                                            None, None)
            print(
                f"Notified frame processing module about disconnection of client {client_address}.")

    def log_error(self, client_address, error):
        print(f"Error handling client {client_address}: {error}")
        if self.frame_processing_module.new_frame_callback is not None:
            self.frame_processing_module \
                .new_frame_callback(client_address, None, None)

    def cleanup_connection(self, client_socket, client_address):
        client_socket.close()
        if self.frame_processing_module.new_frame_callback is not None:
            self.frame_processing_module \
                .new_frame_callback(client_address, None, None)
