import threading

from GUI.student_gui import ClientGUI
from GUI.teacher_gui import ServerGUI

if __name__ == "__main__":
    # Start the server
    server_gui = ServerGUI('192.168.68.106', 4532)
    threading.Thread(target=server_gui.run, daemon=True).start()

    # Start the client
    client_gui = ClientGUI('192.168.68.106', 4532)
    client_gui.run()
