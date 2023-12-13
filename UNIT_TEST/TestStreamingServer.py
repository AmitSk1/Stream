import unittest
from unittest.mock import patch, MagicMock
from server import StreamingServer  # Make sure to import your actual server class

class TestStreamingServer(unittest.TestCase):

    def setUp(self):
        # Set up a server instance with a mock for the new_frame_callback
        self.server = StreamingServer('127.0.0.1', 8000, new_frame_callback=MagicMock())

    @patch('server.socket.socket')
    def test_start_server(self, mock_socket):
        # Test if the server starts and listens correctly
        self.server.start_server()
        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        self.assertTrue(self.server.running)
        self.server.server_socket.listen.assert_called_once()

    @patch('server.socket.socket')
    def test_accept_connections(self, mock_socket):
        # Test if the server accepts connections correctly
        # This test needs to be careful to not enter an infinite loop
        with patch.object(self.server, 'running', new_callable=MagicMock(return_value=True)):
            mock_socket.return_value.accept.return_value = (MagicMock(), ('127.0.0.1', 8001))
            self.server.accept_connections()
            mock_socket.return_value.accept.assert_called_once()

    @patch('server.socket.socket')
    @patch('server.threading.Thread')
    def test_client_handler(self, mock_thread, mock_socket):
        # Test client handler for correct data handling
        mock_client_socket = MagicMock()
        mock_address = ('127.0.0.1', 8001)
        self.server.client_handler(mock_client_socket, mock_address)
        # Assuming a certain sequence of bytes should be sent by the client
        # You need to replace b'' with the actual byte sequence expected
        mock_client_socket.recv.assert_called_with(server.RECEIVE_BUFFER_SIZE)
        # Test that the client_handler spawned a thread
        mock_thread.assert_called()

    @patch('server.socket.socket')
    def test_stop_server(self, mock_socket):
        # Test if the server stops correctly
        self.server.start_server()
        self.server.stop_server()
        self.assertFalse(self.server.running)
        self.server.server_socket.close.assert_called_once()

# Run the tests
if __name__ == '__main__':
    unittest.main()
