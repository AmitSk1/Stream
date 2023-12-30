SIZE_TO_FILL = 5
MIN_SIZE = 0
def send(socket, data):
    """
    send the files in chunk
    """
    encoded_msg = data.encode()
    l = len(encoded_msg)
    ll = str(l)
    lll = ll.zfill(SIZE_TO_FILL)
    llll = lll.encode()
    socket.send(llll + encoded_msg)


def recv(sock):
    """
    receive a socket read 4 byte from socket message
    """
    TOTAL_SIZE = b""
    SIZE = 4
    TOTAL_DATA = b""
    while SIZE > MIN_SIZE:
        data = sock.recv(SIZE)
        SIZE -= len(data)
        TOTAL_SIZE = TOTAL_SIZE + data
    SIZE = int(TOTAL_SIZE.decode())
    while SIZE > MIN_SIZE:
        data = sock.recv(SIZE)
        SIZE -= len(data)
        TOTAL_DATA += data
    return TOTAL_DATA.decode()


def send_bin(sock, data):
    lenn = len(data)
    size_str = str(lenn).zfill(SIZE_TO_FILL)
    sock.send(size_str.encode('utf-8'))  # Send size info
    sock.send(data)  # Send actual data

def recv_bin(sock):
    data_size_bytes = sock.recv(SIZE_TO_FILL)
    data_size_str = data_size_bytes.decode('utf-8')
    if not data_size_str.isdigit():
        raise ValueError(f"Invalid data size received: {data_size_bytes}")

    size = int(data_size_str)
    tot_data = b''
    while size > 0:
        part = sock.recv(size)
        if not part:
            raise ConnectionError("Connection closed during data reception")
        tot_data += part
        size -= len(part)

    return tot_data