
"""
student_gui
Amit Skarbin
"""
from tkinter import Tk, StringVar, Label, Entry, Button, messagebox, Toplevel
from client1 import StreamingClient


class ClientGUI:
    """
    A GUI for the student client to enter their name and start streaming.
    """

    def __init__(self, host, port):
        """
        Initializes the ClientGUI with a StreamingClient.
        """
        self.client = StreamingClient(host, port)
        self.window = Tk()
        self.window.title("Student GUI")
        # Initialize the StringVar for username
        self.username_var = StringVar()
        self.setup_gui()

    def setup_gui(self):
        """Sets up the GUI components for the client."""
        self.client.connect_to_server()
        self.label = Label(self.window, text="Enter your name:")
        self.label.pack()

        self.entry = Entry(self.window, textvariable=self.username_var)
        self.entry.pack()

        self.button = Button(self.window, text="Start Streaming",
                             command=self.start_streaming)
        self.button.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_streaming(self):
        """Starts the streaming process with the entered username."""
        username = self.username_var.get()
        if username:
            self.client.start_stream(username)
            self.create_control_window()

    def on_closing(self):
        """Handles the GUI window closing event."""
        if messagebox.askokcancel("Quit", "Do you want to exit?"):
            self.client.stop_client()
            self.window.destroy()

    def finish_test(self):
        """Stops the streaming process."""
        self.client.stop_client()
        self.window.destroy()

    def create_control_window(self):
        """
        Creates a control window that allows the user to stop the stream.
        """
        self.control_window = Toplevel(self.window)
        self.control_window.title("Streaming Control")
        Label(self.control_window, text="Streaming is running...").pack()
        stop_button = Button(self.control_window, text="Finish Test",
                             command=self.finish_test)
        stop_button.pack()

    def run(self):
        """Runs the main loop of the GUI."""
        self.window.mainloop()


if __name__ == "__main__":
    gui = ClientGUI('127.0.0.1', 1254)
    gui.run()