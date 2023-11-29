"""
teacher_gui
Amit Skarbin
"""
import threading
from tkinter import Tk, Button, messagebox, Label
from server1 import StreamingServer


class ServerGUI:
    """
    A GUI for the teacher's dashboard to control the streaming server.
    """

    def __init__(self, host, port):
        """
        Initializes the ServerGUI with a StreamingServer.
        """
        self.server = StreamingServer(host, port)
        self.window = Tk()
        self.window.title("Teacher's Dashboard")
        self.setup_gui()

    def setup_gui(self):
        """Sets up the GUI  for the server control."""
        self.start_server()
        self.label = Label(self.window, text="Waiting for students to connect")
        self.label.pack()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_server(self):
        """Starts the server in a separate thread."""
        threading.Thread(target=self.server.start_server, daemon=True).start()

    def on_closing(self):
        """Handles the GUI window closing event."""
        if messagebox.askokcancel(
                "Quit", "Do you want to shut down the server?"):
            self.server.stop_server()
            self.window.destroy()

    def run(self):
        """Runs the main loop of the GUI."""
        self.window.mainloop()


if __name__ == "__main__":
    gui = ServerGUI('127.0.0.1', 1254)
    gui.run()