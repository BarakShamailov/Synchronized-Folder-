import tkinter as tk
import threading
import socket
from PIL import Image, ImageTk
from tkinter import filedialog ,messagebox,ttk ,simpledialog
import os
from auxiliary_methods import fix_path,path_up,calculate_size, calculate_checksum, check_length_name, check_illegal_name, check_length_path
DEFAULT_PORT = 9999
default_ip = socket.gethostbyname(socket.gethostname())
ROOT_PATH = 'Path: home/'
FOLDER_TYPE = "●[Folder]"
class ClientGui:


    def __init__(self):
        self.port = None
        self.SIZE = 1024
        self.is_disconnected = False

        self.ip = None
        self.server_address = None

        self.ip_checked = None
        self.check_button_ip = None
        self.text_ip_address = None
        self.port_checked = None
        self.check_port = None
        self.text_port = None

        self.var = None
        self.format = "utf-8"
        self.client_dir_data = "client_data/"
        self.server_dir_data = "server_data"

        self.text_port = None
        self.text_user_name = None
        self.upload_btn = None
        self.text_ip_address = None

        self.counter_files = 0
        self.window = tk.Tk()
        self.window.geometry("800x600")
        self.window.minsize(800,600)
        self.window.maxsize(width=800, height=600)
        self.window.title("Sharing Folder")

        self.window.icon = tk.PhotoImage(file="media/client_icon.png")
        self.window.iconphoto(True, self.window.icon)
        self.image = Image.open("media/background.png")
        self.image = self.image.resize((280, 125))
        self.logo = ImageTk.PhotoImage(self.image)

        self.login()
        self.window.mainloop()


    def login(self):

        self.image_label = tk.Label(self.window, image=self.logo)
        self.image_label.place(x=270, y=20)

        ip_address_label = tk.Label(self.window, text="IP Address", bg="lightgray", fg="black", font=("Segoe UI", 14), relief="solid",bd=1)
        ip_address_label.place(x=340,y=195,width=120,height=35)

        self.text_ip_address = tk.Entry(self.window)
        self.text_ip_address.place(x=300,y=240,width=200,height=30)

        self.ip_checked = tk.BooleanVar()
        self.check_button_ip = tk.Checkbutton(self.window, text=f"Use my local IP",variable=self.ip_checked,command=self.clicked_check_ip)
        self.check_button_ip.place(x=500, y=245)

        port_label = tk.Label(self.window, text="Port", bg="lightgray", fg="black", font=("Segoe UI", 14), relief="solid",bd=1)
        port_label.place(x=350, y=290,width=100)

        self.text_port = tk.Entry(self.window)
        self.text_port.place(x=300, y=330,width=200,height=30)

        self.port_checked = tk.BooleanVar()
        self.check_port = tk.Checkbutton(self.window, text=f"Use default port",variable=self.port_checked,command=self.clicked_check_port)
        self.check_port.place(x=500, y=335)

        login_btn = tk.Button(self.window,text='Login',bg='lightgrey'	, fg="black", font=("Segoe UI", 10),
                              command=self.main_window)
        login_btn.place(x=325, y=500, width=150, height=40)


    def clicked_check_ip(self):
        if self.ip_checked.get():
            self.text_ip_address.config(state=tk.DISABLED)
            self.ip = default_ip

        else:
            self.text_ip_address.config(state=tk.NORMAL)
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

    def main_window(self):
        self.clicked_check_ip()
        self.clicked_check_port()
        self.server_address = (self.ip, self.port)
        if not self.connect_to_server(self.server_address):
            self.clean_window()
            self.login()
        else:
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.clean_window()
            self.label_path = ttk.Label(self.window, text=f"{ROOT_PATH}", background="white", foreground="black",font=("Segoe UI",10))
            self.label_path.place(x=5, y=5,width=680,height=20)

            self.columns = ("No.", "Name", "Size", "Modified Date")
            self.tree = ttk.Treeview(self.window, columns=self.columns, show="headings", height=24, )

            # Set column headings
            for col in self.columns:
                self.tree.heading(col, text=col)

            # Set column widths
            self.tree.column("No.", width=70, anchor="center")
            self.tree.column("Name", width=350, anchor="center")
            self.tree.column("Size", width=150, anchor="center")
            self.tree.column("Modified Date", width=205, anchor="center")

            self.tree.place(x=0, y=32)

            scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
            scrollbar.place(x=780, y=32, height=510)
            self.tree.configure(yscrollcommand=scrollbar.set)
            self.tree.bind("<<TreeviewSelect>>")



            self.folder_logo = tk.PhotoImage(file="media/folder_icon.png")
            self.new_folder_btn = tk.Button(self.window,image=self.folder_logo, compound='left',command=self.clicked_newfolder_btn)
            self.new_folder_btn.place(x=760, y=0,width=40,height=30)

            self.arrow_logo = tk.PhotoImage(file="media/arrow_up.png")
            self.arrow_btn = tk.Button(self.window, image=self.arrow_logo, compound='left',command=self.clicked_arrow_btn)
            self.arrow_btn.place(x=726, y=0, width=30, height=30)

            self.refresh_logo = tk.PhotoImage(file="media/refresh.png")
            self.refresh_btn = tk.Button(self.window, image=self.refresh_logo, compound='left',command=self.clicked_refresh_btn)
            self.refresh_btn.place(x=690, y=0, width=30, height=30)

            self.upload_file_btn = tk.Button(self.window, bg="lightgray", text='Upload File', fg="black", font=("Segoe UI", 10),command=self.clicked_upload_file_btn)
            self.upload_file_btn.pack(ipadx=50, ipady=10)
            self.upload_file_btn.place(x=715, y=550)

            self.upload_folder_btn = tk.Button(self.window, bg="lightgray", text='Upload Folder', fg="black",
                                             font=("Segoe UI", 10), command=self.clicked_upload_folder_btn)
            self.upload_folder_btn.pack(ipadx=50, ipady=10)
            self.upload_folder_btn.place(x=610, y=550)

            download_btn = tk.Button(self.window, bg="lightgray", text='Download', fg="black", font=("Segoe UI", 10),command=self.clicked_download_btn)
            download_btn.pack(ipadx=50, ipady=10)
            download_btn.place(x=530, y=550)

            open_btn = tk.Button(self.window, bg="lightgray", text='Open', fg="black", font=("Segoe UI", 10),command=self.clicked_open_btn)
            open_btn.pack(ipadx=50, ipady=10)
            open_btn.place(x=10, y=550)

            delete_btn = tk.Button(self.window, bg="lightgray", text='Delete', fg="black", font=("Segoe UI", 10), command=self.clicked_delete_btn)
            delete_btn.pack(ipadx=50, ipady=10)
            delete_btn.place(x=60, y=550)

            move_btn = tk.Button(self.window, bg="lightgray", text='Move to', fg="black", font=("Segoe UI", 10),
                                   command=self.clicked_move_btn)
            move_btn.pack(ipadx=50, ipady=10)
            move_btn.place(x=190, y=550)

            rename_btn = tk.Button(self.window, bg="lightgray", text='Rename', fg="black", font=("Segoe UI", 10),command=self.clicked_rename_btn)
            rename_btn.pack(ipadx=50, ipady=10)
            rename_btn.place(x=120, y=550)

            self.present_server_files()
            self.receive_thread = threading.Thread(target=self.receive_data_from_server,daemon=True)
            self.receive_thread.start()

    def clicked_move_btn(self):
        self.client.send("MOVE".encode(self.format))

    def clicked_upload_folder_btn(self):
        self.client.send("UPLOAD_FOLDER".encode(self.format))

    def clicked_newfolder_btn(self):
        self.client.send("FOLDER".encode(self.format))

    def clicked_refresh_btn(self):
        self.client.send("REFRESH".encode(self.format))

    def clicked_arrow_btn(self):
        self.client.send("ARROW".encode(self.format))

    def clicked_upload_file_btn(self):
        self.client.send("UPLOAD".encode(self.format))

    def clicked_rename_btn(self):
        self.client.send("RENAME".encode(self.format))

    def clicked_delete_btn(self):
        self.client.send("DELETE".encode(self.format))

    def clicked_download_btn(self):
        self.client.send("DOWNLOAD".encode(self.format))

    def clicked_open_btn(self):
        self.client.send("OPEN".encode(self.format))

    def receive_data_from_server(self):
            while True:
                try:
                    data = self.client.recv(self.SIZE).decode(self.format)
                    if data == "UPLOAD":
                        self.upload_file()
                    elif data == "RENAME":
                        self.rename_file()
                    elif data == "DELETE":
                        self.delete_file()
                    elif data == "DOWNLOAD":
                        self.download_file()
                    elif data == "OPEN":
                        self.open_file()
                    elif data == "UPDATE" or data == "REFRESH":
                        self.present_server_files()
                    elif data == "FOLDER":
                        self.create_folder()
                    elif data == "UPLOAD_FOLDER":
                        self.upload_folder()
                    elif data == "OPEN":
                        self.open_file()
                    elif data == "MOVE":
                        self.move_file()
                    elif data == "ARROW":
                        self.arrow_up()
                    elif data == "DISCONNECT":
                        self.is_disconnected = True
                        messagebox.showinfo("Info",message=f"The server is offline now.\nYou have been disconnected.")
                        break
                        # Process the received data as needed
                except Exception as e:
                    messagebox.showerror(message=f"Error receiving message: {e}")
                    break



    def arrow_up(self):
        current_path = self.label_path.cget("text")
        if current_path == ROOT_PATH:
            self.client.send("ERROR".encode(self.format))
            messagebox.showerror(message=f"You are already in the root folder.")
        else:
            data = f"OK@{current_path}"
            self.client.send(data.encode(self.format))
            receive_data_server = self.client.recv(self.SIZE).decode(self.format)
            if receive_data_server == "DONE":
                server_msg = self.client.recv(self.SIZE).decode(self.format)
                if server_msg == "UPDATE":
                    new_path = path_up(self.label_path.cget("text"))
                    self.label_path.config(text=new_path)
                    self.present_server_files()


    def upload_file(self):
        file_path = filedialog.askopenfilename()  # Open a file dialog to select a file
        if file_path != '':
            is_file_in_server = self.sending_data_to_server(file_path)
            if not is_file_in_server:
                file_name = file_path.split('/')[-1]
                messagebox.showinfo("Info", message=f"The {file_name} was uploaded successfully.")
                server_msg = self.client.recv(self.SIZE).decode(self.format)
                if server_msg == "UPDATE":
                    self.present_server_files()
                # Display the selected file path in a label or process the file as needed
                self.counter_files += 1

        else:
            self.client.send("ERROR".encode(self.format))

    def on_closing(self):
        try:
            if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
                if not self.is_disconnected:
                    self.client.send("DISCONNECT".encode(self.format))
                self.client.close()
                self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", message=f"Occur error '{e}' when trying to disconnect.")
            self.window.destroy()
    def sending_data_to_server(self,path,server_path=""):
        cmd = "UPLOAD"
        file_name = path.split("/")[-1]
        file_size = os.path.getsize(path)
        if server_path == "":
            server_path = fix_path(self.label_path.cget("text"))
        file_checksum = calculate_checksum(path)
        send_data = f"{cmd}@{file_name}@{str(file_size)}@{server_path}@{file_checksum}"
        self.client.send(send_data.encode(self.format))
        server_msg = self.client.recv(self.SIZE).decode(self.format)
        if server_msg == "EXISTS":
            user_choice = tk.messagebox.askquestion("Replace", f"The file {file_name} has already exits.\nDo you want to replace {file_name}?")
            if user_choice == 'yes':
                cmd = "REPLACE"
                self.client.send(cmd.encode(self.format))
            else:
                self.client.send("DONE".encode(self.format))
                return True
        uploading_label = tk.Label(self.window, text="Uploading...", font=("Segoe UI", 10), bg="lightblue", bd=1,relief="solid")
        uploading_label.place(x=300, y=555, width=200)
        with open(path, "rb") as file:
             while True:
                 if file_size < self.SIZE:
                     data = file.read(file_size)
                     if not data:
                         self.client.send(b"END")
                         break
                     else:
                         self.client.send(data)
                 else:
                     data = file.read(self.SIZE)
                     if not data:
                         self.client.send(b"END")
                         break
                     else:
                         self.client.send(data)
        uploading_label.destroy()
        server_msg = self.client.recv(self.SIZE).decode(self.format)
        if server_msg == "ERROR":
            messagebox.showerror("Error", message=f"There was a problem: \nthe file was not created successfully or is not valid on the server.")
            cmd = "ERROR"
            self.client.send(cmd.encode(self.format))
            return False
        else:
            cmd = "OK"
            self.client.send(cmd.encode(self.format))
        return False


    def present_server_files(self):
        self.clear_files()
        cmd = "LIST"
        self.client.send(cmd.encode(self.format))
        self.client.recv(self.SIZE).decode(self.format)
        path = fix_path(self.label_path.cget("text"))
        self.client.send(path.encode(self.format))
        data = self.client.recv(self.SIZE).decode(self.format)
        amount_files = int(data)
        len_info = []
        # Receiving the size exactly size of the data
        for i in range(0, amount_files):
            data = self.client.recv(self.SIZE).decode(self.format)
            self.client.send("OK".encode(self.format))
            len_info.append(len(data))
        # Receiving the data
        for i in range(amount_files):
            data = self.client.recv(len_info[i]).decode(self.format)
            file_name, file_size, modified_time, type = data.split("@")
            self.counter_files += 1
            if type == 'folder':
                self.tree.insert("", tk.END, values=(FOLDER_TYPE, file_name, file_size, modified_time))
            else:
                self.tree.insert("", tk.END, values=( f"{self.counter_files}", file_name, calculate_size(file_size), modified_time))

    def delete_file(self):
        is_marked = False
        selected_items = self.tree.selection()
        for item in selected_items:
            values = self.tree.item(item, "values")
            is_marked = True
            file_to_delete = values[1]
            file_type = values[0]
            path = fix_path(self.label_path.cget("text"))
            send_data = f"{file_to_delete}@{file_type}@{path}"
            self.client.send(send_data.encode(self.format))
            server_msg = self.client.recv(self.SIZE).decode(self.format)
            if server_msg == "IN_USE":
                messagebox.showerror("Error",message=f"Can't delete {file_to_delete} is in use by another user.")
                self.tree.selection_remove(self.tree.selection())
                break
            elif server_msg == "NOT_EXIST":
                messagebox.showerror("Error", message=f"Can't find the file, perhaps its name has been renamed or the file has been deleted or has been moved.\nrefreshing.")
                self.tree.selection_remove(self.tree.selection())
                break
            else:
                messagebox.showinfo("Info",message=f"The {file_to_delete} item has been deleted.")

        if not is_marked:
            self.client.send("NO_MARKED".encode(self.format))
            messagebox.showerror("Error", "No file has been selected.")

        else:
            self.client.send("DONE".encode(self.format))
            receive_data_server = self.client.recv(self.SIZE).decode(self.format)
            if receive_data_server == "DONE":
                self.present_server_files()


    def clear_files(self):
        self.counter_files = 0
        self.tree.delete(*self.tree.get_children())

    def rename_file(self):
        is_marked = False
        user_choice = False
        new_name = None
        selected_items = self.tree.selection()
        for item in selected_items:
            values = self.tree.item(item, "values")
            is_marked = True
            file_to_rename = values[1]
            file_type = values[0]
            path = fix_path(self.label_path.cget("text"))
            send_data = f"{path}@{file_to_rename}@{file_type}"
            self.client.send(send_data.encode(self.format))
            server_msg = self.client.recv(self.SIZE).decode(self.format)
            if server_msg == "IN_USE":
                messagebox.showerror("Error", message=f"Can't rename the {file_to_rename} is in use.")
                self.tree.selection_remove(self.tree.selection())
                break
            data_file = file_to_rename.split(".")
            valid_name, valid_length_name = True, True
            newWin = tk.Tk()
            newWin.geometry("800x600")
            newWin.withdraw()
            while valid_name or valid_length_name:
                new_name = simpledialog.askstring("Rename File", f"Enter the new name for {file_to_rename} :",
                                                  parent=newWin)
                if new_name is None:
                    self.tree.selection_remove(self.tree.selection())
                    user_choice = True
                    break
                valid_name = check_illegal_name(new_name)
                valid_length_name = check_length_name(new_name)
            if user_choice:
                break
            newWin.destroy()
            if file_type != FOLDER_TYPE:
                new_name += "." + data_file[-1]
            send_data = f"{new_name}"
            self.client.send(send_data.encode(self.format))
            server_msg = self.client.recv(self.SIZE).decode(self.format)

            if server_msg == "NOT_EXIST":
                messagebox.showerror("Error", message=f"Can't find the file, perhaps its name has been renamed or the file has been deleted or has been moved.\nrefreshing.")
                self.tree.selection_remove(self.tree.selection())
                break
            elif server_msg == "EXISTS":
                messagebox.showerror("Error", message=f"There is a file/folder with the same name.\nPlease pick different other name.")
                self.tree.selection_remove(self.tree.selection())
                break
            else:
                self.tree.selection_remove(self.tree.selection())
                messagebox.showinfo("Info",message=f"The {file_to_rename} has been renamed to - {new_name}.")

        if not is_marked:
            self.client.send("NO_MARKED".encode(self.format))
            messagebox.showerror("Error", "No file has been selected.")
        elif user_choice:
            self.client.send("NO_NAME".encode(self.format))
        else:
            self.client.send("DONE".encode(self.format))
            receive_data_server = self.client.recv(self.SIZE).decode(self.format)
            if receive_data_server == "DONE":
                self.present_server_files()


    def connect_to_server(self,address):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect(address)
            return True
        except:
            messagebox.showerror("Error", "Connection Failed.\nPlease try again.")
            return False



    def download_file(self):
        is_marked = False
        selected_items = self.tree.selection()
        counter = 0
        max_time_to_ask = 1
        file_path, save_file, = None, None
        for item in selected_items:
            values = self.tree.item(item, "values")
            is_marked = True
            if values[0] == FOLDER_TYPE:
                messagebox.showerror("Error", message=f"It is not possible to download folders, only files.")
                self.client.send("ERROR".encode(self.format))
            else:
                send_data = f"{values[0]}@{values[1]}"
                self.client.send(send_data.encode(self.format))
                server_msg = self.client.recv(self.SIZE).decode(self.format)
                if server_msg == "OK":
                    if counter < max_time_to_ask:
                        file_path = filedialog.askdirectory(title="Please select a folder to download the files to.")
                        counter += 1
                    if file_path == '' or file_path is None:
                        self.client.send("ERROR".encode(self.format))
                        break
                    else:
                        save_file = values[1]
                        path = fix_path(self.label_path.cget("text"))
                        send_data = f"path@{path}"
                        self.client.send(send_data.encode(self.format))
                        server_msg = self.client.recv(self.SIZE).decode(self.format)
                        if server_msg == "NOT_EXIST":
                            messagebox.showerror("Error", message=f"It is not exist anymore, please refresh.")
                            self.tree.selection_remove(self.tree.selection())
                            break
                        else:
                            downloading_label = tk.Label(self.window, text="Downloading...", font=("Segoe UI", 10),bg="lightblue", bd=1, relief="solid")
                            downloading_label.place(x=300, y=555, width=200)
                            new_path = file_path + "/" + save_file
                            with open(new_path, "wb") as file:
                                while True:
                                    data = self.client.recv(self.SIZE)
                                    if data[-3:] == b'END':
                                        file.write(data[:len(data) - 3])
                                        break
                                    file.write(data)
                            self.tree.selection_remove(self.tree.selection())
                            messagebox.showinfo("Info", message=f"The {save_file} file downloading has been finished.")
                            downloading_label.destroy()
                else:
                    messagebox.showerror("Error", message=f"The file: {values[1]} cannot be downloaded as it is currently in use by another user.")
                    self.tree.selection_remove(self.tree.selection())
                    break

        if not is_marked:
            self.client.send("NO_MARKED".encode(self.format))
            messagebox.showerror("Error", "No file has been selected.")
        else:
            self.client.send("DONE".encode(self.format))



    def open_file(self):
        is_marked = False
        selected_items = self.tree.selection()
        counter = 0
        max_files_chosen = 1
        for item in selected_items:
            if counter == max_files_chosen:
                messagebox.showerror("Error", message=f"Can't open two folders, only one.")
                break
            values = self.tree.item(item, "values")
            is_marked = True
            if values[0] == FOLDER_TYPE:
                data = fix_path(self.label_path.cget("text") + values[1])
                self.client.send(data.encode(self.format))
                receive_data_server = self.client.recv(self.SIZE).decode(self.format)
                if receive_data_server == "DONE":
                    self.label_path.config(text=self.label_path.cget("text") + values[1] + "/")
                    self.present_server_files()
                    counter += 1
                elif receive_data_server == "NOT_EXIST":
                    messagebox.showerror("Error", message=f"It is not exist anymore, refreshing.")
                    self.tree.selection_remove(self.tree.selection())
                    self.present_server_files()
                    break
            else:
                messagebox.showerror("Error", message=f"It is not possible to open files, only folders.")
                self.client.send("ERROR".encode(self.format))
                break

        # Check is_marked after the loop
        if not is_marked:
            messagebox.showerror("Error", "No file has been selected.")

    def move_file(self):
        is_marked, user_choice, error = False, False, False
        folder_name, server_msg = None, None
        counter = 1
        selected_items = self.tree.selection()
        for item in selected_items:
            values = self.tree.item(item, "values")
            is_marked = True
            file_name = values[1]
            file_type = values[0]
            path = fix_path(self.label_path.cget("text"))
            send_data = f"{path}@{file_name}@{file_type}"
            self.client.send(send_data.encode(self.format))
            server_msg = self.client.recv(self.SIZE).decode(self.format)
            if server_msg == "IN_USE":
                messagebox.showerror("Error", message=f"Can't move  the {file_name} is in use by another user.")
                self.tree.selection_remove(self.tree.selection())
                error = True
                break
            if server_msg == "NOT_EXIST":
                messagebox.showerror("Error", message=f"Can't find the file, perhaps its name has been renamed or the file has been deleted or has been moved.\nrefreshing.")
                self.tree.selection_remove(self.tree.selection())
                error = True
                break
            newWin = tk.Tk()
            newWin.geometry("800x600")
            newWin.withdraw()
            while counter == 1:
                folder_name = simpledialog.askstring("Move",
                                                     f"Please write the name of the folder that you want to move the files to: ",
                                                     parent=newWin)
                if folder_name is None:
                    self.tree.selection_remove(self.tree.selection())
                    user_choice = True
                    break
                elif folder_name == "":
                    messagebox.showerror("Error",
                                         message=f"Please insert name.")
                else:
                    counter += 1
                    break
            if user_choice:
                break
            newWin.destroy()
            if folder_name == file_name:
                messagebox.showerror("Error",
                                     message=f"You can't move folder to itself.")
                self.tree.selection_remove(self.tree.selection())
                error = True
                break
            if folder_name == path.split('/')[-2]:
                messagebox.showerror("Error",
                                     message=f"The file is already in the folder - {folder_name}.")
                self.tree.selection_remove(self.tree.selection())
                error = True
                break
            folder_name = "server_data" if folder_name == "home" else folder_name
            send_data = f"{folder_name}"
            self.client.send(send_data.encode(self.format))
            server_msg = self.client.recv(self.SIZE).decode(self.format)
            if server_msg == "NOT_EXIST":
                messagebox.showerror("Error",
                                     message=f"The name of the folder that you entered is not exists, please try again.")
                self.tree.selection_remove(self.tree.selection())
                error = True
                break
            elif server_msg == "EXISTS":
                messagebox.showerror("Error",
                                     message=f"In the folder to which you want to transfer the file - {file_name}, there is already a file with the same name."
                                             f"\nThe file name must be changed before the transfer.")
                self.tree.selection_remove(self.tree.selection())
                error = True
                break
            else:
                self.tree.selection_remove(self.tree.selection())
        if not is_marked:
            self.client.send("NO_MARKED".encode(self.format))
            messagebox.showerror("Error", "No file has been selected.")
        elif user_choice:
            self.client.send("NO_NAME".encode(self.format))
        else:
            self.client.send("DONE".encode(self.format))
            receive_data_server = self.client.recv(self.SIZE).decode(self.format)
            if receive_data_server == "DONE":
                if not error:
                    folder_name = "home" if folder_name == "server_data" else folder_name
                    messagebox.showinfo("Info",message=f"The transfer to the folder: {folder_name}, was successful.")
                self.present_server_files()

    def create_folder(self):
        user_choice = False
        valid_name, valid_length_name  = True, True
        new_name , server_msg = None, None
        newWin = tk.Tk()
        newWin.geometry("800x600")
        newWin.withdraw()
        while valid_name or valid_length_name:
            new_name = simpledialog.askstring("Folder", f"Write the folder's name: ",
                                              parent=newWin)
            if new_name is None:
                self.tree.selection_remove(self.tree.selection())
                user_choice = True
                break
            valid_name = check_illegal_name(new_name)
            valid_length_name = check_length_name(new_name)
        newWin.destroy()
        path = fix_path(self.label_path.cget("text"))
        data = f"{path}@{new_name}"
        if check_length_path(data):
            user_choice = True
        if not user_choice:
            self.client.send(data.encode(self.format))
            server_msg = self.client.recv(self.SIZE).decode(self.format)

            if server_msg == "OK":
                messagebox.showinfo("Info",message=f"The folder {new_name} was created successfully.")
            else:
                self.client.send("EXISTS".encode(self.format))
                messagebox.showerror("Error",
                                     message="There is a folder with the same name.\nPlease pick different other name.")
        if server_msg != "EXISTS":
            if user_choice:
                self.client.send("NO_NAME".encode(self.format))
            else:
                self.client.send("DONE".encode(self.format))
                receive_data_server = self.client.recv(self.SIZE).decode(self.format)
                if receive_data_server == "DONE":
                    self.present_server_files()

    def upload_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder")
        if folder_path:
            self.client.send("FOLDER".encode(self.format))
            data = self.client.recv(self.SIZE).decode(self.format)
            if data == 'FOLDER':
                folder_name = folder_path.split('/')[-1]
                path = fix_path(self.label_path.cget("text"))
                data = f"{path}@{folder_name}"
                self.client.send(data.encode(self.format))
                server_msg = self.client.recv(self.SIZE).decode(self.format)
                if server_msg == "OK":
                    self.client.send("DONE".encode(self.format))
                else:
                    self.client.send("EXISTS".encode(self.format))
                server_msg = self.client.recv(self.SIZE).decode(self.format)
                if server_msg == "DONE":
                    files_folder = os.listdir(folder_path)
                    for file in files_folder:
                        self.client.send("UPLOAD".encode(self.format))
                        server_msg = self.client.recv(self.SIZE).decode(self.format)
                        if server_msg == "UPLOAD":

                            file_path = folder_path + '/' + file
                            server_path = path+folder_name+'/'
                            self.sending_data_to_server(file_path,server_path)
                            server_msg = self.client.recv(self.SIZE).decode(self.format)
                            if server_msg == "UPDATE":
                                continue
                    messagebox.showinfo("Info", message=f"The folder {folder_name} was uploaded successfully.")
                    self.counter_files += 1
                    self.present_server_files()
                else:
                    messagebox.showerror("Error",
                                         message="There is a folder with the same name.\nPlease pick different other name.")
        else:
            self.client.send("ERROR".encode(self.format))



if __name__ == "__main__":
    ClientGui()

