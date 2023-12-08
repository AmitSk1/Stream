import threading
import tkinter as tk
from tkinter import Frame, Label, messagebox

import cv2
from PIL import Image, ImageTk
import math
from server1 import StreamingServer  # Ensure this import matches your file structure

class ServerGUI:
    def __init__(self, host, port):
        self.server = StreamingServer(host, port, self.new_frame_received)
        self.window = tk.Tk()
        self.window.title("Teacher's Dashboard")
        self.student_frames = {}
        self.setup_gui()

    def setup_gui(self):
        Label(self.window, text="Waiting for student to connect...").pack()
        self.start_server()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.streams_frame = Frame(self.window)
        self.streams_frame.pack(fill=tk.BOTH, expand=True)

    def new_frame_received(self, client_address, frame):
        student_id = f"{client_address[0]}:{client_address[1]}"
        if student_id not in self.student_frames:
            self.add_student_stream(student_id)
        self.update_video_display(student_id, frame)

    def add_student_stream(self, student_id):
        frame = Frame(self.streams_frame, bg='black', width=200, height=120)
        frame.pack_propagate(False)
        video_label = tk.Label(frame)
        video_label.pack(fill=tk.BOTH, expand=True)
        self.student_frames[student_id] = video_label
        frame.grid(row=0, column=len(self.student_frames)-1)
        self.update_layout()

    def update_video_display(self, student_id, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(frame)
        if student_id in self.student_frames:
            self.student_frames[student_id].config(image=frame)
            self.student_frames[student_id].image = frame

    def update_layout(self):
        num_students = len(self.student_frames)
        rows, cols = self.calculate_grid_dimensions(num_students)
        for i, frame in enumerate(self.student_frames.values()):
            frame.grid(row=i // cols, column=i % cols, sticky='nsew')
        for r in range(rows):
            self.streams_frame.grid_rowconfigure(r, weight=1)
        for c in range(cols):
            self.streams_frame.grid_columnconfigure(c, weight=1)

    def calculate_grid_dimensions(self, num_students):
        cols = round(math.sqrt(num_students))
        rows = math.ceil(num_students / cols)
        return rows, cols

    def start_server(self):
        threading.Thread(target=self.server.start_server, daemon=True).start()
        print("Starting server ")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to shut down the server?"):
            self.server.stop_server()
            self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    gui = ServerGUI('127.0.0.1', 8000)
    gui.run()
