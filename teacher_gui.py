"""
teacher_gui
Amit Skarbin
"""
import threading
import tkinter as tk
from tkinter import Tk, Button, messagebox, Frame
from server1 import StreamingServer
import math


class ServerGUI:
    """
    A GUI for the teacher's dashboard to control the streaming server.
    """

    def __init__(self, host, port):
        """
        Initializes the ServerGUI with a StreamingServer.
        """
        self.server = StreamingServer(host, port)
        self.window = tk.Tk()
        self.window.title("Teacher's Dashboard")
        self.student_frames = {}  # Dictionary to hold student frames
        self.setup_gui()

    def setup_gui(self):
        """Sets up the GUI  for the server control."""
        Button(self.window, text="Start Server",
               command=self.start_server).pack()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Create a frame to hold the student video streams
        self.streams_frame = Frame(self.window)
        self.streams_frame.pack(fill=tk.BOTH, expand=True)

    def add_student_stream(self, student_id):
        """Adds a new student stream to the GUI."""
        frame = Frame(self.streams_frame, bg='black', width=200, height=120)
        frame.pack_propagate(False)  # Prevents frame resizing to fit widgets
        # Label or Video Widget would go here
        label = tk.Label(frame, text=f"Student {student_id}", bg='black', fg='white')
        label.pack(fill=tk.BOTH, expand=True)

        self.student_frames[student_id] = frame
        self.update_layout()

    def remove_student_stream(self, student_id):
        """Removes a student stream from the GUI."""
        frame = self.student_frames.pop(student_id, None)
        if frame:
            frame.destroy()
            self.update_layout()

    def update_layout(self):
        """Updates the layout of student streams."""
        num_students = len(self.student_frames)
        rows, cols = self.calculate_grid_dimensions(num_students)
        for i, frame in enumerate(self.student_frames.values()):
            frame.grid(row=i // cols, column=i % cols, sticky='nsew')

        for r in range(rows):
            self.streams_frame.grid_rowconfigure(r, weight=1)
        for c in range(cols):
            self.streams_frame.grid_columnconfigure(c, weight=1)

    def calculate_grid_dimensions(self, num_students):
        """Calculate the number of rows and columns for the grid."""
        cols = round(math.sqrt(num_students))
        rows = math.ceil(num_students / cols)
        return rows, cols

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
