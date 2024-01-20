"""
Client GUI
Amit Skarbin

A GUI for the student client to enter their name and start streaming.
"""

import os
from tkinter import Tk, StringVar, Label, Entry, Button, messagebox, \
    Toplevel, Frame, filedialog
from Client_Modules.client import StreamingClient


class ClientGUI:
    """
    GUI class for the client application.

    This class creates a graphical user interface for the client to control
    the video streaming and file operations to the server.
    """

    def __init__(self, host, port):
        """
        Initializes the ClientGUI with a StreamingClient.

        Args:
            The server IP address.
            The port number on which the server is listening.
        """
        self.client = StreamingClient(host, port)
        self.window = Tk()
        self.window.title("Student GUI")
        self.username_var = StringVar()
        self.setup_gui()

    def setup_gui(self):
        """
        Sets up the GUI components for the client.
        """
        main_frame = Frame(self.window)
        main_frame.pack(padx=10, pady=10)

        Label(main_frame, text="Enter your name:").grid(row=0, column=0,
                                                        sticky='w')
        Entry(main_frame, textvariable=self.username_var).grid(row=0, column=1,
                                                               sticky='ew')
        Button(main_frame, text="Start Streaming", command=self.
               start_streaming).grid(row=1, column=0, columnspan=2, pady=5)

        main_frame.grid_columnconfigure(1, weight=1)
        download_button = Button(self.window, text="Download File",
                                 command=self.download_file)
        download_button.pack()

        upload_button = Button(main_frame, text="Upload File",
                               command=self.select_file_to_upload)
        upload_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_streaming(self):
        """
        Starts the video streaming process with the entered username.
        """
        username = self.username_var.get()
        if username:
            self.client.start_stream(username)
            self.create_control_window()

    def on_closing(self):
        """
        Handles the event when the GUI window is closing.
        """
        if messagebox.askokcancel("Quit", "Do you want to exit?"):
            self.client.stop_client()
            self.window.destroy()

    def finish_test(self):
        """
        Stops the streaming process.
        """
        self.client.stop_client()
        self.window.destroy()

    def create_control_window(self):
        """
        Creates a control window to allow the user to stop the stream.
        """
        self.control_window = Toplevel(self.window)
        self.control_window.title("Streaming Control")
        Label(self.control_window, text="Streaming is running...").pack()
        stop_button = Button(self.control_window, text="Finish Test",
                             command=self.finish_test)
        stop_button.pack()

    def select_file_to_upload(self):
        """
        Opens a file dialog to select a file and uploads it to the server.
        """
        username = self.username_var.get()
        file_path = filedialog.askopenfilename()
        if file_path:
            self.client.file_management_module.upload_file(file_path, username)
            messagebox.showinfo("Upload", "File upload to the teacher.")

    def download_file(self):
        """
        Requests the last file from the server and saves it to a specified
        directory.
        """
        self.client.file_management_module.request_last_file()
        directory = "C:/testKeeper"
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.client.file_management_module.receive_file_from_server(directory)
        messagebox.showinfo("Download Complete", f"File saved to {directory}")
        print("Download Complete", f"File saved to {directory}")

    def run(self):
        """
        Runs the main loop of the GUI.
        """
        self.window.mainloop()


if __name__ == "__main__":
    gui = ClientGUI('192.168.68.106', 4532)
    gui.run()
