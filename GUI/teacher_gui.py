import threading
import tkinter as tk
from tkinter import Frame, Label, messagebox
from PIL import Image, ImageTk
import math
from server import StreamingServer  # Make sure this import matches your project structure
import cv2


class ServerGUI:
    def __init__(self, host, port, resolution=(640, 480)):  # Example resolution (width x height)
        self.server = StreamingServer(host, port, self.new_frame_received)
        self.window = tk.Tk()
        self.window.title("Teacher's Dashboard")
        self.resolution = resolution
        self.aspect_ratio = resolution[1] / resolution[0]
        self.student_frames = {}
        self.setup_gui()


    def setup_gui(self):
        self.streams_frame = Frame(self.window)
        self.streams_frame.pack(fill=tk.BOTH, expand=True)  # Use pack here for the main frame only
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.bind('<Configure>', self.on_window_resize)  # Bind the resize event
        self.start_server()

    def on_window_resize(self, event=None):
        # Called whenever the window is resized
        self.update_layout()

    def start_server(self):
        threading.Thread(target=self.server.start_server, daemon=True).start()
        print("start server")

    def new_frame_received(self, client_address, frame):
        student_id = f"{client_address[0]}:{client_address[1]}"
        if student_id not in self.student_frames:
            self.add_student_stream(student_id)
        self.update_video_display(student_id, frame)

    def add_student_stream(self, student_id):
        frame_label = Label(self.streams_frame)
        # Use grid to manage the layout of student frames within self.streams_frame
        # Initially place the frame out of view; it will be positioned by update_layout
        frame_label.grid(row=999, column=999)
        self.student_frames[student_id] = frame_label
        self.update_layout()

    def new_frame_received(self, client_address, frame):
        student_id = f"{client_address[0]}:{client_address[1]}"
        if student_id not in self.student_frames:
            self.add_student_stream(student_id)
        self.update_video_display(student_id, frame)
        self.update_layout()

    def remove_student_stream(self, student_id):
        if student_id in self.student_frames:
            frame_label = self.student_frames[student_id]
            frame_label.grid_forget()  # Remove the frame from the grid
            frame_label.destroy()  # Destroy the frame widget
            del self.student_frames[student_id]  # Remove the reference
            self.update_layout()  # Update the layout since a stream was removed

    def update_video_display(self, student_id, frame):
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_image = Image.fromarray(frame)
            frame_photo = ImageTk.PhotoImage(image=frame_image)
            self.student_frames[student_id].configure(image=frame_photo)
            self.student_frames[student_id].image = frame_photo  # Keep a reference
        else:
            # Handle the case where the client has disconnected
            self.remove_student_stream(student_id)

    def update_layout(self):
        num_students = len(self.student_frames)
        if num_students == 0:
            return  # Exit if there are no student streams

        # Get the window's current width and height
        window_width = self.streams_frame.winfo_width()
        window_height = self.streams_frame.winfo_height()

        # Calculate the appropriate number of columns and rows
        cols = min(5, num_students)  # Set the maximum number of columns
        rows = math.ceil(num_students / cols)

        # Calculate the size of each frame
        frame_width = window_width // cols
        frame_height = int(frame_width * self.aspect_ratio)  # Maintain the aspect ratio

        # Check if the total height exceeds the window height and adjust if necessary
        total_height = frame_height * rows
        if total_height > window_height:
            frame_height = window_height // rows
            frame_width = int(frame_height / self.aspect_ratio)

        # Update the size and position of each frame
        for i, (student_id, frame_label) in enumerate(self.student_frames.items()):
            row = i // cols
            col = i % cols
            frame_label.grid(row=row, column=col, sticky='nsew')

            # Remove any previous photo images to avoid holding onto deleted references
            frame_label.image = None

        # Adjust the configuration of each grid cell
        for r in range(rows):
            self.streams_frame.grid_rowconfigure(r, weight=1)
        for c in range(cols):
            self.streams_frame.grid_columnconfigure(c, weight=1)
    def calculate_grid_dimensions(self, num_students):
        cols = min(5, math.ceil(math.sqrt(num_students)))  # Limit the number of columns to a maximum of 5
        rows = math.ceil(num_students / cols)
        return rows, cols

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to shut down the server?"):
            self.server.stop_server()
            self.window.destroy()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = ServerGUI('192.168.68.111', 4532)
    gui.run()
