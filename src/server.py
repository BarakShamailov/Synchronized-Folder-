import tkinter as tk
import socket
import os
import shutil
from datetime import datetime
import threading
from tkinter import messagebox
from auxiliary_methods import check_file_or_folder, check_path, calculate_checksum, check_move_file_folder

DEFAULT_PORT = 9999
default_ip = socket.gethostbyname(socket.gethostname())
SIZE = 1024
FORMAT = "utf-8"
FOLDER_TYPE = "●[Folder]"
server_dir_data = "server_data/"
open_files = []
clients = []
open_folders = []
client_handlers = []

lock = threading.Lock()
class ServerGui:
    def __init__(self):
        self.ip = None
        self.port = None
        self.server_address = None
        self.server = None
        self.done = True

        self.window = tk.Tk()
        self.window.geometry("800x600")
        self.window.minsize(800, 600)
        self.window.maxsize(width=800, height=600)


        self.window.title("Server")
        self.counter_rows = 1

        self.window.icon = tk.PhotoImage(file="media/server_icon.png")
        self.window.iconphoto(True, self.window.icon)
        self.setup_win()
        self.window.mainloop()

    def setup_win(self):

        ip_address_label = tk.Label(self.window, text="IP Address",fg="black", font=("Segoe UI", 14,"bold"), relief="solid",bd=1)
        ip_address_label.place(x=340,y=50,width=120,height=35)

        self.text_ip_address = tk.Entry(self.window)
        self.text_ip_address.place(x=300,y=95,width=200,height=30)

        self.ip_checked = tk.BooleanVar()
        self.check_button_ip = tk.Checkbutton(self.window,fg="black",text=f"Use my local IP",variable=self.ip_checked,command=self.clicked_check_ip)
        self.check_button_ip.place(x=500, y=100)

        port_label = tk.Label(self.window, text="Port", fg="black", font=("Segoe UI", 14,"bold"), relief="solid",bd=1)
        port_label.place(x=350, y=155,width=100)

        self.text_port = tk.Entry(self.window)
        self.text_port.place(x=300, y=200,width=200,height=30)

        self.port_checked = tk.BooleanVar()
        self.check_port = tk.Checkbutton(self.window,fg="black", text=f"Use default port",variable=self.port_checked,command=self.clicked_check_port)
        self.check_port.place(x=500, y=205)

        setup_btn = tk.Button(self.window,text='Setup server', fg="black", font=("Segoe UI", 10),
                              command=self.msgs_win)
        setup_btn.place(x=325, y=500, width=150, height=40)

    def clicked_check_ip(self):
        if self.ip_checked.get():
            self.text_ip_address.config(state=tk.DISABLED)
            self.ip = default_ip

        else:
            self.text_ip_address.config(state=tk.NORMAL)
            if len(self.text_ip_address.get()) > 0:
                self.ip = self.text_ip_address.get()

    def clicked_check_port(self):
        if self.port_checked.get():
            self.text_port.config(state=tk.DISABLED)
            self.port = DEFAULT_PORT
        else:
            self.text_port.config(state=tk.NORMAL)
            if len(self.text_port.get()) > 0:
                self.port = int(self.text_port.get())

    def clean_window(self):

        for widget in self.window.winfo_children():
            widget.destroy()


    def msgs_win(self):
        self.clicked_check_ip()
        self.clicked_check_port()
        self.server_address = (self.ip, self.port)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.configure(bg="black")
        self.users_label = tk.Label(self.window, text=f"Active users : {len(clients)}", bg="black", fg="white", font=("Segoe UI", 12))
        self.users_label.place(x=670, y=0)

        ip_label = tk.Label(self.window, text=f"IP : {self.ip}", bg="black", fg="white", font=("Segoe UI", 12))
        ip_label.place(x=5, y=0)

        port_label = tk.Label(self.window, text=f"Port : {self.port}", bg="black", fg="white", font=("Segoe UI", 12))
        port_label.place(x=5, y=20)

        server_label = tk.Label(self.window, text="Server History", bg="black", fg="green", font=("Segoe UI", 22))
        server_label.place(x=300, y=5)

        # To create a text widget and specify size.
        self.t = tk.Text(self.window, bg="black", height=26, width=85, fg="green", font=("Segoe UI", 12))
        self.t.place(x=10, y=50)

        # Create a scrollbar and associate it with the Text widget
        self.scrollbar = tk.Scrollbar(self.window, command=self.t.yview)
        self.scrollbar.place(x=780, y=50, height=550)

        # Configure the Text widget to work with the Scrollbar
        self.t.config(yscrollcommand=self.scrollbar.set)

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.server_address)
            self.server.listen()
        except Exception as e:
            messagebox.showerror("Error", f"There is problem to setup the server.\nPlease check the IP and the Port that you entered and try again.")
            exit()

        self.setup_server = threading.Thread(target=self.setup_server, daemon=True)
        self.setup_server.start()


    def setup_server(self):


        # Listen for incoming connections
        self.insert_text("Starting Server...")
        self.insert_text("Waiting for a connection...")
        while self.done:
            try:
                connection, client_address = self.server.accept()
                clients.append(connection)
                self.client_handler = threading.Thread(target=self.handle_client, daemon=True,args=(connection, client_address))
                self.client_handler.start()
                client_handlers.append(self.client_handler)
                self.insert_text(f"The client {client_address} connected")
                self.users_label.config(text=f"Active users : {len(clients)}")
            except Exception as e:
                messagebox.showerror("Error", f"There is problem to setup the server {e}.")
                break

    def insert_text(self, message):
        # Insert text into the Text widget
        quote = f"#{self.counter_rows} {message}\n"
        self.t.insert(tk.END, quote)
        self.counter_rows += 1

        # Automatically scroll to the bottom
        self.t.see(tk.END)

    def handle_client(self,connection, client_address):

        while self.done:
            try:
                cmd = connection.recv(SIZE).decode(FORMAT)

                if cmd == "UPLOAD":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.receive_file(connection)

                elif cmd == "RENAME":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.rename_server_file(connection)

                elif cmd == "LIST":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.file_details_in_server(connection)

                elif cmd == "REFRESH":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.refresh_files(connection)

                elif cmd == "MOVE":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.move_files_to_folder(connection)

                elif cmd == "DELETE":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.delete_server_file(connection)

                elif cmd == "DOWNLOAD":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.send_file(connection)

                elif cmd == "FOLDER":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.create_sub_folder(connection)

                elif cmd == "UPLOAD_FOLDER":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.receive_folder(connection)

                elif cmd == "OPEN":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.open_file_server(connection)

                elif cmd == "ARROW":
                    self.insert_text(f"The client {client_address} sent {cmd} request")
                    self.up_dir_path(connection)
                    connection.send("UPDATE".encode(FORMAT))

                elif cmd == "DISCONNECT":
                    self.insert_text(f"The client {client_address} disconnected")
                    clients.remove(connection)
                    connection.close()
                    self.users_label.config(text=f"Active users : {len(clients)}")
                    break
            except Exception as e:
                self.insert_text(f"Error: '{e}'")
                clients.remove(connection)
                self.users_label.config(text=f"Active users : {len(clients)}")
                break

    def refresh_files(self, client_socket):
        client_socket.send("REFRESH".encode(FORMAT))

    def open_file_server(self,client_socket):
        client_socket.send("OPEN".encode(FORMAT))
        data = client_socket.recv(SIZE).decode(FORMAT)
        while True:
            if not check_path(data):
                cmd = "NOT_EXIST"
                client_socket.send(cmd.encode(FORMAT))
                break
            elif data == "ERROR":
                break
            else:
                folder = data.split("/")
                lock.acquire()
                open_folders.append(folder[-1])
                lock.release()
                client_socket.send("DONE".encode(FORMAT))
                break

    def move_files_to_folder(self, client_socket):
        client_socket.send("MOVE".encode(FORMAT))
        path, file_name, file_type, folder_name = None, None, None, None
        items_in_use = list()
        while True:
            data = client_socket.recv(SIZE).decode(FORMAT)
            if '@' in data:
                path, file_name, file_type = data.split("@")
                if not check_path(path+file_name):
                    cmd = "NOT_EXIST"
                    client_socket.send(cmd.encode(FORMAT))
                    continue
                if file_type == FOLDER_TYPE and file_name not in open_folders:
                    lock.acquire()
                    open_folders.append(file_name)
                    items_in_use.append(file_name)
                    lock.release()
                    client_socket.send("OK".encode(FORMAT))
                    continue
                elif file_type != FOLDER_TYPE and file_name not in open_files:
                    lock.acquire()
                    open_files.append(file_name)
                    items_in_use.append(file_name)
                    lock.release()
                    client_socket.send("OK".encode(FORMAT))
                    continue
                else:
                    client_socket.send("IN_USE".encode(FORMAT))
                    continue
            if data == "DONE":
                cmd = "DONE"
                client_socket.send(cmd.encode(FORMAT))
                self.remove_open_files_dirs(items_in_use)
                break
            elif data == "NO_MARKED":
                self.remove_open_files_dirs(items_in_use)
                break
            elif data == "NO_NAME":
                self.remove_open_files_dirs(items_in_use)
                break
            else:
                folder_name = data
                is_folder_in_path, folder_path = check_move_file_folder(path, folder_name)
                if not is_folder_in_path:
                    folder_path = path + folder_name
                if not check_path(folder_path):
                    cmd = "NOT_EXIST"
                    client_socket.send(cmd.encode(FORMAT))
                    continue
                if self.checking_exists_file_move(is_folder_in_path,file_name,folder_name,path,folder_path):
                    cmd = "EXISTS"
                    client_socket.send(cmd.encode(FORMAT))
                    continue
                source_path = path + file_name
                destination_path = folder_path+file_name
                if not is_folder_in_path:
                    destination_path = path + folder_name + '/' + file_name

                if file_type != FOLDER_TYPE:
                    # Move the file by renaming it
                    os.rename(source_path, destination_path)
                    client_socket.send("DONE".encode(FORMAT))
                else:
                    # Move the folder using shutil.move
                    shutil.move(source_path, destination_path)
                    client_socket.send("DONE".encode(FORMAT))

    def up_dir_path(self,client_socket):
        client_socket.send("ARROW".encode(FORMAT))
        data = client_socket.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        if data[0] == "OK":
            folder_out = data[1].split('/')
            self.out_critical_folder(folder_out[-2])
            client_socket.send("DONE".encode(FORMAT))

    def create_sub_folder(self,client_socket):
        client_socket.send("FOLDER".encode(FORMAT))
        while True:
            data = client_socket.recv(SIZE).decode(FORMAT)
            path, folder_name = None, None
            if '@' in data:
                path, folder_name = data.split('@')
            if data == "DONE":
                cmd = "DONE"
                client_socket.send(cmd.encode(FORMAT))
                break
            elif data == 'NO_NAME':
                break
            elif data == "EXISTS":
                break
            else:
                try:
                    os.makedirs(path + folder_name)
                    client_socket.send("OK".encode(FORMAT))
                except FileExistsError:
                    client_socket.send("EXISTS".encode(FORMAT))

    def on_closing(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            for connection in clients:
                try:
                    connection.send("DISCONNECT".encode(FORMAT))
                    connection.close()
                except Exception as e:
                    self.insert_text(f"Error closing connection: {e}")
            self.done = False
            self.server.close()
            self.window.destroy()
    def send_file(self,client_socket):
        client_socket.send("DOWNLOAD".encode(FORMAT))
        file_name, path = None, None
        items_in_use = []
        while True:
            data = client_socket.recv(SIZE).decode(FORMAT)
            if data == "DONE":
                break
            elif data == "NO_MARKED":
                self.remove_open_files_dirs(items_in_use)
                break
            elif data == "ERROR":
                self.remove_open_files_dirs(items_in_use)
                break
            else:
                data = data.split("@")
                if data[0] == "path":
                    path = data[1]
                elif data[0] != FOLDER_TYPE:
                    file_type = data[0]
                    file_name = data[1]
                    if file_type != FOLDER_TYPE and file_name not in open_files:
                        lock.acquire()
                        open_files.append(file_name)
                        items_in_use.append(file_name)
                        lock.release()
                        client_socket.send("OK".encode(FORMAT))
                        continue
                    else:
                        client_socket.send("IN_USE".encode(FORMAT))
                        continue
                new_path = path + file_name
                if not check_path(new_path):
                    cmd = "NOT_EXIST"
                    client_socket.send(cmd.encode(FORMAT))
                    continue
                client_socket.send("OK".encode(FORMAT))
                with open(new_path, "rb") as file:
                    while True:
                        data = file.read(SIZE)
                        if not data:
                            client_socket.send(b"END")
                            break
                        else:
                            client_socket.send(data)
                self.remove_open_files_dirs(items_in_use)

    def delete_server_file(self,client_socket):
        client_socket.send("DELETE".encode(FORMAT))
        file_name, file_type, path = None, None, None
        while True:
            data = client_socket.recv(SIZE).decode(FORMAT)
            if '@' in data:
                file_name, file_type, path = data.split('@')
                if not check_path(path+file_name):
                    cmd = "NOT_EXIST"
                    client_socket.send(cmd.encode(FORMAT))
                    continue
            # Checking if the file is open
            if data == "DONE":
                cmd = "DONE"
                client_socket.send(cmd.encode(FORMAT))
                break
            elif data == "NO_MARKED":
                break
            else:
                if file_type != FOLDER_TYPE:
                    if file_name not in open_files:
                        lock.acquire()
                        open_files.append(file_name)
                        lock.release()
                        # Delete the file
                        new_path = path + file_name
                        os.remove(new_path)
                        self.out_critical_files(file_name)
                        client_socket.send("OK".encode(FORMAT))
                    else:
                        client_socket.send("IN_USE".encode(FORMAT))
                    continue
                else:
                    if file_name not in open_folders:
                        lock.acquire()
                        open_folders.append(file_name)
                        lock.release()
                        new_path = path + file_name
                        # delete folder
                        shutil.rmtree(new_path)
                        client_socket.send("OK".encode(FORMAT))
                        self.out_critical_folder(file_name)
                    else:
                        client_socket.send("IN_USE".encode(FORMAT))
                    continue

    def file_details_in_server(self,client_socket):
        client_socket.send("LIST".encode(FORMAT))
        folder_path = client_socket.recv(SIZE).decode(FORMAT)
        file_names = os.listdir(folder_path[:len(folder_path) - 1])
        amount_files = len(file_names)
        client_socket.send(str(amount_files).encode(FORMAT))
        # The goal of the first loop is to send the length of the data
        for i in range(0, len(file_names)):
            file_path = os.path.join(folder_path, file_names[i])
            type_file = check_file_or_folder(file_path)
            size = os.path.getsize(file_path)
            size = str(size)
            if type_file == 'folder':
                size = '---'
            # Convert the modification time to a readable format without seconds
            modification_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d-%m-%y %H:%M')
            send_data = f"{file_names[i]}@{size}@{modification_time}@{type_file}"
            client_socket.send(send_data.encode(FORMAT))
            data = client_socket.recv(SIZE).decode(FORMAT)
        # The goal of the second loop is to send data
        for i in range(0, amount_files):
            file_path = os.path.join(folder_path, file_names[i])
            type_file = check_file_or_folder(file_path)
            size = os.path.getsize(file_path)
            size = str(size)
            if type_file == 'folder':
                size = '---'
            # Convert the modification time to a readable format without seconds
            modification_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d-%m-%y %H:%M')
            send_data = f"{file_names[i]}@{size}@{modification_time}@{type_file}"
            client_socket.send(send_data.encode(FORMAT))

    def receive_folder(self, client_socket):
        client_socket.send("UPLOAD_FOLDER".encode(FORMAT))
        data = client_socket.recv(SIZE).decode(FORMAT)
        if data == 'FOLDER':
            client_socket.send("FOLDER".encode(FORMAT))
            while True:
                data = client_socket.recv(SIZE).decode(FORMAT)
                path, folder_name = None, None
                if '@' in data:
                    path, folder_name = data.split('@')
                if data == "DONE":
                    client_socket.send(data.encode(FORMAT))
                    break
                elif data == "EXISTS":
                    client_socket.send(data.encode(FORMAT))
                    break
                else:
                    try:
                        os.makedirs(path + folder_name)
                        client_socket.send("OK".encode(FORMAT))
                    except FileExistsError:
                        client_socket.send("EXISTS".encode(FORMAT))
            if data != "EXISTS":
                data = client_socket.recv(SIZE).decode(FORMAT)
                if data == "UPLOAD":
                    self.receive_file(client_socket)

    def receive_file(self,client_socket):
        client_socket.send("UPLOAD".encode(FORMAT))
        while True:
            data = client_socket.recv(SIZE).decode(FORMAT)
            if data == "ERROR":
                break
            if data == "OK":
                client_socket.send("UPDATE".encode(FORMAT))
                break
            cmd, file_name, file_size, path, client_file_checksum = data.split("@")
            file_size = int(file_size)
            new_path = path + file_name
            if cmd == "UPLOAD":
                file_names = os.listdir(path)
                if file_name in file_names:
                    client_socket.send("EXISTS".encode(FORMAT))
                    data = client_socket.recv(SIZE).decode(FORMAT)
                    if data == "REPLACE":
                        os.remove(new_path)
                        with open(new_path, "wb") as file:
                            while True:
                                if file_size < SIZE:
                                    data = client_socket.recv(file_size)
                                    if data[-3:] == b'END':
                                        file.write(data[:len(data) - 3])
                                        break
                                    file.write(data)
                                else:
                                    data = client_socket.recv(SIZE)
                                    if data[-3:] == b'END':
                                        file.write(data[:len(data) - 3])
                                        break
                                    file.write(data)
                        server_file_checksum = calculate_checksum(new_path)
                        if server_file_checksum == client_file_checksum:
                            client_socket.send("OK".encode(FORMAT))
                        else:
                            os.remove(new_path)
                            client_socket.send("ERROR".encode(FORMAT))
                        continue
                    else:
                        break
                else:
                    client_socket.send("OK".encode(FORMAT))
                    with open(new_path, "wb") as file:
                        while True:
                            if file_size < SIZE:
                                data = client_socket.recv(file_size)
                                if data[-3:] == b"END":
                                    file.write(data[:len(data) - 3])
                                    break
                                file.write(data)
                            else:
                                data = client_socket.recv(SIZE)
                                if data[-3:] == b"END":
                                    file.write(data[:len(data)-3])
                                    break
                                file.write(data)
                    server_file_checksum = calculate_checksum(new_path)
                    if server_file_checksum == client_file_checksum:
                        client_socket.send("OK".encode(FORMAT))
                    else:
                        os.remove(new_path)
                        client_socket.send("ERROR".encode(FORMAT))
                    continue

    def rename_server_file(self,client_socket):
        client_socket.send("RENAME".encode(FORMAT))
        file_to_rename, file_type, new_name, path = None, None, None, None
        items_in_use = []
        while True:
            data = client_socket.recv(SIZE).decode(FORMAT)
            if '@' in data:
                path, file_to_rename, file_type = data.split("@")
                if file_type == FOLDER_TYPE and file_to_rename not in open_folders:
                    lock.acquire()
                    open_folders.append(file_to_rename)
                    items_in_use.append(file_to_rename)
                    lock.release()
                    client_socket.send("OK".encode(FORMAT))
                    continue
                elif file_type != FOLDER_TYPE and file_to_rename not in open_files:
                    lock.acquire()
                    open_files.append(file_to_rename)
                    items_in_use.append(file_to_rename)
                    lock.release()
                    client_socket.send("OK".encode(FORMAT))
                    continue
                else:
                    client_socket.send("IN_USE".encode(FORMAT))
                    continue
            if data == "DONE":
                cmd = "DONE"
                client_socket.send(cmd.encode(FORMAT))
                self.remove_open_files_dirs(items_in_use)
                break
            elif data == "NO_MARKED":
                self.remove_open_files_dirs(items_in_use)
                break
            elif data == "NO_NAME":
                self.remove_open_files_dirs(items_in_use)
                break
            else:
                new_name = data
                old_file_path = path + file_to_rename  # The file path to rename
                if not check_path(old_file_path):
                    cmd = "NOT_EXIST"
                    client_socket.send(cmd.encode(FORMAT))
                    continue
                new_file_path = os.path.dirname(old_file_path) + '/' + new_name
                if check_path(new_file_path):
                    cmd = "EXISTS"
                    client_socket.send(cmd.encode(FORMAT))
                    continue
                os.rename(old_file_path, new_file_path)
                client_socket.send("DONE".encode(FORMAT))

    def out_critical_files(self,file_name):
        with lock:
            if file_name in open_files:
                open_files.remove(file_name)

    def out_critical_folder(self,folder_name):
        with lock:
            if folder_name in open_folders:
                open_folders.remove(folder_name)

    def checking_exists_file_move(self,is_folder_in_path, file_name, folder_name, path,folder_path):

        if not is_folder_in_path:
            if file_name in os.listdir(path + folder_name + '/'):
                return True

        else:
            if file_name in os.listdir(folder_path):
                return True
        return False

    def remove_open_files_dirs(self,items):
        for item in items:
            self.out_critical_files(item)
            self.out_critical_folder(item)


# Instantiate the ServerGui class and run the application
if __name__ == "__main__":
    server_app = ServerGui()

