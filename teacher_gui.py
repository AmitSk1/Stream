import threading
import tkinter as tk
from tkinter import Frame, Label, messagebox
from PIL import Image, ImageTk
import math
from server1 import StreamingServer  # Make sure this import matches your project structure
import cv2


class ServerGUI:
    def __init__(self, host, port, resolution=(640, 480)):  # Example resolution (width x height)
        self.server = StreamingServer(host, port, self.new_frame_received)
        self.window = tk.Tk()
        self.window.title("Teacher's Dashboard")
        self.resolution = resolution
        self.student_frames = {}
        self.setup_gui()

    def setup_gui(self):
        self.streams_frame = Frame(self.window)
        self.streams_frame.pack(fill=tk.BOTH, expand=True)
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
        frame_label.pack(fill=tk.BOTH, expand=True)
        self.student_frames[student_id] = frame_label
        self.update_layout()

    def new_frame_received(self, client_address, frame):
        student_id = f"{client_address[0]}:{client_address[1]}"
        if frame is None:
            # If frame is None, remove the student's frame because they have disconnected
            self.remove_student_stream(student_id)
        else:
            if student_id not in self.student_frames:
                self.add_student_stream(student_id)
            self.update_video_display(student_id, frame)

    def remove_student_stream(self, student_id):
        if student_id in self.student_frames:
            frame_label = self.student_frames[student_id]
            frame_label.grid_forget()  # Remove the frame from the grid
            frame_label.destroy()  # Destroy the frame widget
            del self.student_frames[student_id]  # Remove the reference from the dictionary
            self.update_layout()  # Update the layout since the number of frames has changed

    def update_video_display(self, student_id, frame):
        # Convert the frame from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert the frame to a format that Tkinter can use
        frame_image = Image.fromarray(frame_rgb)
        frame_photo = ImageTk.PhotoImage(image=frame_image)
        # Update the Label widget with the new image
        if student_id in self.student_frames:
            self.student_frames[student_id].configure(image=frame_photo)
            self.student_frames[student_id].image = frame_photo  # Keep a reference to prevent garbage-collection

    def update_layout(self):
        num_students = len(self.student_frames)
        if num_students == 0:
            return  # Avoid division by zero when there are no students

        # Get the new window size
        window_width = self.streams_frame.winfo_width()
        window_height = self.streams_frame.winfo_height()

        # Determine the number of rows and columns, with a maximum of 5 columns
        cols = min(5, num_students)
        rows = math.ceil(num_students / cols)

        # Calculate the size of each frame, maintaining the aspect ratio
        aspect_ratio = self.resolution[1] / self.resolution[0]  # height / width
        frame_width = window_width // cols
        frame_height = int(frame_width * aspect_ratio)

        # Update the size and position of each frame
        for i, (student_id, frame_label) in enumerate(self.student_frames.items()):
            row = i // cols
            col = i % cols
            frame_label.grid(row=row, column=col, sticky='nsew')
            frame_label.config(width=frame_width, height=frame_height)  # This sets the size of the frame

        # Configure weight for each row and column to make them expandable
        for r in range(rows):
            self.streams_frame.grid_rowconfigure(r, weight=1)
        for c in range(cols):
            self.streams_frame.grid_columnconfigure(c, weight=1)

    def calculate_grid_dimensions(self, num_students):
        cols = min(5, math.ceil(math.sqrt(num_students)))
        rows = math.ceil(num_students / cols)
        return rows, cols

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to shut down the server?"):
            self.server.stop_server()
            self.window.destroy()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = ServerGUI('192.168.68.111', 4567)
    gui.run()
