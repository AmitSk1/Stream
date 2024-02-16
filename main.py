from GUI.student_gui import ClientGUI
from GUI.teacher_gui import ServerGUI


if __name__ == "__main__":
    # Start the server
    gui = ServerGUI('192.168.68.111', 4532)
    gui.run()

    # Start the client
    client_gui = ClientGUI('192.168.68.111', 4532)
    client_gui.run()