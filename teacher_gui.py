import threading
import tkinter as tk
from tkinter import Frame, Label, messagebox
from PIL import Image, ImageTk
import math
from server import StreamingServer
import cv2


class ServerGUI:
    """
    GUI for the teacher to monitor video streams from students.
    """

    def __init__(self, host, port, resolution=(640, 480)):
        """
        Initializes the server GUI with the server and display settings.
        """
        self.server = StreamingServer(host, port, self.new_frame_received)
        self.window = tk.Tk()
        self.window.title("Teacher's Dashboard")
        self.resolution = resolution
        self.aspect_ratio = resolution[1] / resolution[0]
        self.student_frames = {}
        self.student_images = {}
        self.fullscreen_student_id = None
        self.setup_gui()

    def setup_gui(self):
        """
        Sets up the initial graphical user interface for the server.
        """
        self.streams_frame = Frame(self.window)
        self.streams_frame.pack(fill=tk.BOTH, expand=True)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.bind('<Configure>', self.on_window_resize)
        self.start_server()

    def on_window_resize(self, event=None):
        """
        Responds to the window resize event to update the layout of
        video streams.
        """
        self.update_layout()

    def start_server(self):
        """
        Starts the streaming server in a separate thread.
        """
        threading.Thread(target=self.server.start_server, daemon=True).start()
        print("Starting streaming server")

    def add_student_stream(self, student_id):
        """
        Adds a new student stream to the GUI.
        """
        frame_label = Label(self.streams_frame)
        frame_label.bind('<Double-Button-1>',
                         lambda e, sid=student_id: self.toggle_fullscreen(sid))
        frame_label.grid(row=999, column=999)  # Initially place out of view
        self.student_frames[student_id] = frame_label
        self.update_layout()

    def toggle_fullscreen(self, student_id):
        """
        Toggles the fullscreen mode for a selected student stream.
        """
        if self.fullscreen_student_id:  # If already in fullscreen, minimize
            self.fullscreen_student_id = None
            self.window.attributes('-fullscreen', False)
            self.update_layout()
        else:  # If not in fullscreen, maximize this student's stream
            self.fullscreen_student_id = student_id
            self.maximize_student_stream(student_id)

    def maximize_student_stream(self, student_id):
        """
        Maximizes the stream of a selected student to fill the entire window.

        Args:
            student_id (str): The unique identifier of the student.
        """
        # Hide all frames
        for sid, frame_label in self.student_frames.items():
            frame_label.grid_forget()

        # Show only the selected student's
        # frame and expand it to fill the window
        frame_label = self.student_frames[student_id]
        frame_label.grid(row=0, column=0, sticky='nsew')

        # Adjust grid configuration to occupy the entire window
        self.streams_frame.grid_rowconfigure(0, weight=1)
        self.streams_frame.grid_columnconfigure(0, weight=1)

        # Update the window layout immediately
        self.streams_frame.update_idletasks()

        # Calculate the dimensions to resize the video frame
        window_width = self.streams_frame.winfo_width()
        window_height = self.streams_frame.winfo_height()

        # Set the size of the frame label to the window size
        frame_label.config(width=window_width, height=window_height)

    def new_frame_received(self, client_address, frame, username):
        """
        Handles new frames received from clients.
        """
        student_id = f"{client_address[0]}:{client_address[1]}"
        if frame is None:
            self.remove_student_stream(student_id)
            if self.fullscreen_student_id == student_id:
                self.fullscreen_student_id = None
                self.window.attributes('-fullscreen', False)
        else:
            self.window.after(0, self.update_video_display,
                              student_id, frame, username)

    def remove_student_stream(self, student_id):
        """
        Removes a student's stream from the GUI.
        """
        if student_id in self.student_frames:
            frame_label = self.student_frames[student_id]
            frame_label.grid_forget()
            frame_label.destroy()
            del self.student_frames[student_id]
            self.update_layout()

    def update_video_display(self, student_id, frame, username):
        """
        Updates the video display with a new frame from a student.
        """
        # Check if the frame is not None and the
        # student_id is in student_frames
        if frame is not None and student_id in self.student_frames:
            # Resize the frame if the student is in fullscreen mode
            if self.fullscreen_student_id == student_id:
                frame = cv2.resize(frame, (self.streams_frame.winfo_width(),
                                           self.streams_frame.winfo_height()))

        if frame is not None:
            cv2.putText(frame, username, (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_image = Image.fromarray(frame)
            frame_photo = ImageTk.PhotoImage(image=frame_image)

            if student_id not in self.student_frames:
                self.add_student_stream(student_id)

            self.student_frames[student_id].configure(image=frame_photo)
            self.student_frames[student_id].image = frame_photo

    def update_layout(self):
        """
        Updates the layout of the video streams in the GUI.
        """
        if self.fullscreen_student_id:
            self.maximize_student_stream(self.fullscreen_student_id)
            return

        num_students = len(self.student_frames)
        if num_students == 0:
            return

        window_width = self.streams_frame.winfo_width()
        window_height = self.streams_frame.winfo_height()
        cols = int(math.sqrt(num_students))
        rows = math.ceil(num_students / cols)
        frame_width = window_width // cols
        frame_height = window_height // rows

        for i, (student_id, frame_label) in \
                enumerate(sorted(self.student_frames.items())):
            row = i // cols
            col = i % cols
            frame_label.grid(row=row, column=col, sticky='nsew')
            frame_label.config(width=frame_width, height=frame_height)

    def on_closing(self):
        """
        Handles the closing event of the GUI window.
        """
        if messagebox.askokcancel("Quit", "Do you want to "
                                          "shut down the server?"):
            self.server.stop_server()
            self.window.destroy()

    def run(self):
        """
        Runs the main loop of the GUI.
        """
        self.window.mainloop()


if __name__ == "__main__":
    gui = ServerGUI('192.168.68.111', 4532)
    gui.run()
