import threading
import logging
from tkinter import Tk, Button, Listbox, END, messagebox, filedialog
from server1 import StreamingServer


class ServerGUI:
    def __init__(self, host, port):
        self.server = StreamingServer(host, port)
        self.window = Tk()
        self.window.title("Teacher's Dashboard")
        self.setup_gui()

    def send_file_to_students(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            threading.Thread(target=self.server.send_file, args=(file_path,), daemon=True).start()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to shut down the server?"):
            self.server.stop_server()
            self.window.destroy()

    def setup_gui(self):
        Button(self.window, text="Finish Test", command=self.finish_test).pack()
        self.active_students_list = Listbox(self.window)
        self.active_students_list.pack()
        self.active_students_list.pack()

    def run(self):
        threading.Thread(target=self.server.start_server, daemon=True).start()
        self.window.mainloop()

    def finish_test(self):
        self.server.finish_test()


if __name__ == "__main__":
    gui = ServerGUI('127.0.0.1', 2587)
    gui.run()
