"""
Constants
Amit Skarbin
"""
import cv2

# Constants for the client
FPS = 15
RESOLUTION_VERTICAL = 640
RESOLUTION_HORIZONTAL = 360
CAPTURE_DEVICE_INDEX = 0  # Index of the camera capture device
JPEG_COMPRESSION_QUALITY = 50  # Compression quality for JPEG images
PICKLE_PROTOCOL_VERSION = 4  # Protocol version for pickle
# Time to wait between frames, calculated from FPS
WAIT_TIME_PER_FRAME = int(1000 / FPS)

# Constants for the server
PAYLOAD_SIZE_STRUCT_FORMAT = '>L'  # Format for struct packing of payload size
RECEIVE_BUFFER_SIZE = 4096  # Buffer size for receiving data
FRAME_DECODE_COLOR_MODE = cv2.IMREAD_COLOR  # Color mode for frame decoding
KEY_PRESS_CHECK_DELAY = 1  # Delay for checking key press in milliseconds
EXIT_KEY = ord('q')  # Key to press for exiting frame display
