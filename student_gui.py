from tkinter import Tk, StringVar, Label, Entry, Button
from client1 import StreamingClient


class ClientGUI:
    def __init__(self, host, port):
        self.client = StreamingClient(host, port)
        self.window = Tk()
        self.window.title("Student GUI")
        self.setup_gui()

    def setup_gui(self):
        self.client.connect_to_server()
        self.label = Label(self.window, text="Enter your name:")
        self.label.pack()

        self.entry = Entry(self.window, textvariable=self.username_var)
        self.entry.pack()

        self.button = Button(self.window, text="Start Streaming", command=self.start_streaming)
        self.button.pack()

    def start_streaming(self):
        username = self.username_var.get()
        if username:
            self.client.connect_to_server()
            self.client.start_stream(username)
            self.window.destroy()  # Close the configuration window

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = ClientGUI('127.0.0.1', 2587)
    gui.run()