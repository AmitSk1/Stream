import threading
from tkinter import Tk, Button, Listbox, messagebox

from server1 import StreamingServer


class ServerGUI:
    def __init__(self, host, port):
        self.server = StreamingServer(host, port)
        self.window = Tk()
        self.window.title("Teacher's Dashboard")
        self.setup_gui()

    def setup_gui(self):
        Button(self.window, text="Start Server", command=self.start_server).pack()
        self.active_students_list = Listbox(self.window)
        self.active_students_list.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_server(self):
        threading.Thread(target=self.server.start_server, daemon=True).start()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to shut down the server?"):
            self.server.stop_server()
            self.window.destroy()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    gui = ServerGUI('192.168.68.124', 1254)  # Ensure the port here matches the server's port
    gui.run()
