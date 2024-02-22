import os
import hashlib
from tkinter import messagebox
SIZE_KB = 2**10
SIZE_MB = 2**20
SIZE_GB = 2**30
MAX_NAME = 30
MAX_LEN_PATH = 1024
ILLEGAL_LETTERS = ['\\','/',':','*','<','>','?','"','|']

def check_move_file_folder(path,folder_name):
    destination_directory = ""
    is_folder_in_path = False
    folders_in_path = path.split("/")
    for folder in folders_in_path:
        if folder == folder_name:
            destination_directory += folder + '/'
            is_folder_in_path = True
            break
        destination_directory += folder + '/'
    return is_folder_in_path, destination_directory


def check_length_path(path):
    if len(path)>MAX_LEN_PATH:
        messagebox.showerror("Error", "Can't create more folders.\nThe path is too long.")
        return True
    return False


def check_illegal_name(name):
    for i in name:
        if i in ILLEGAL_LETTERS:
            messagebox.showerror("Error", f"File name can't including the next letters:\n{ILLEGAL_LETTERS}.")
            return True
    if name == "":
        messagebox.showerror("Error",
                             message=f"Please insert name.")
        return True
    return False

def check_length_name(name):
    if len(name) > MAX_NAME:
        messagebox.showerror("Error", "The name's length is too long.\nThe max length is 30.")
        return True
    return False


def calculate_size(bytes):
    bytes = int(bytes)
    if bytes < SIZE_KB:
        formatted_result = "{:.2f}".format(bytes)
        return formatted_result + " B"
    elif bytes < SIZE_MB and bytes >= SIZE_KB:
        result = bytes / SIZE_KB
        formatted_result = "{:.2f}".format(result)
        return formatted_result + " KB"
    elif bytes < SIZE_GB and bytes >= SIZE_MB:
        result = bytes / SIZE_MB
        formatted_result = "{:.2f}".format(result)
        return formatted_result + " MB"
    elif bytes >= SIZE_GB:
        result = bytes / SIZE_GB
        formatted_result = "{:.2f}".format(result)
        return formatted_result + " GB"

def check_path(path):
    if os.path.exists(path):
        return True
    else:
        return False
def check_file_or_folder(path):
    if os.path.isfile(path):
        return "file"
    elif os.path.isdir(path):
        return "folder"

def fix_path(path):
    fix_path = path.replace("home","server_data")
    return fix_path.replace("Path: ","")

def path_up(path):
    path_splitted = path.split("/")
    fix_path = '/'.join(path_splitted[:-2])
    return fix_path+'/'


def calculate_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read the file in chunks to handle large files
        for byte_block in iter(lambda: f.read(SIZE_KB), b""):
            sha256.update(byte_block)
    return sha256.hexdigest()


