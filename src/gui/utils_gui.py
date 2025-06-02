import os
import shutil
import socket

import tkinter
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename

from src.face_recognition_utils.model_loader import load_embeddings

import customtkinter

test_dict = {
    1: ["Bob Smith", "02/06/25", "04/06/2025", 95],
    2: ["Alice Johnson", "01/01/24", "05/01/2024", 90],
    3: ["Charlie Brown", "12/03/25", "15/03/2025", 85],
    4: ["Diana Prince", "10/02/25", "12/02/2025", 92],
    5: ["Ethan Hunt", "03/04/25", "07/04/2025", 88],
    6: ["Fiona Gallagher", "05/05/25", "10/05/2025", 91],
    7: ["George Clooney", "09/06/25", "13/06/2025", 87],
    8: ["Hannah Baker", "11/07/25", "14/07/2025", 89],
    9: ["Ivan Drago", "20/01/25", "25/01/2025", 93],
    10: ["Julia Roberts", "17/02/25", "22/02/2025", 86],
    11: ["Kevin Hart", "06/03/25", "09/03/2025", 84],
    12: ["Lana Del Rey", "08/04/25", "11/04/2025", 96],
    13: ["Michael Scott", "15/05/25", "18/05/2025", 88],
    14: ["Nancy Drew", "21/06/25", "24/06/2025", 85],
    15: ["Oscar Wilde", "01/07/25", "03/07/2025", 90],
    16: ["Pam Beesly", "13/08/25", "17/08/2025", 94],
    17: ["Quentin Tarantino", "25/09/25", "29/09/2025", 91],
    18: ["Rachel Green", "10/10/25", "14/10/2025", 89],
    19: ["Steve Rogers", "05/11/25", "09/11/2025", 92],
    20: ["Tony Stark", "16/12/25", "20/12/2025", 95],
    21: ["Uma Thurman", "07/01/25", "10/01/2025", 87],
    22: ["Victor Hugo", "03/02/25", "06/02/2025", 93],
    23: ["Wanda Maximoff", "14/03/25", "17/03/2025", 86],
    24: ["Xander Cage", "09/04/25", "12/04/2025", 88],
    25: ["Yara Shahidi", "18/05/25", "21/05/2025", 90],
    26: ["Zack Snyder", "22/06/25", "25/06/2025", 84],
    27: ["Bruce Wayne", "01/07/25", "04/07/2025", 97],
    28: ["Clark Kent", "11/08/25", "15/08/2025", 89],
    29: ["Donna Paulsen", "13/09/25", "16/09/2025", 91],
    30: ["Elliot Alderson", "17/10/25", "20/10/2025", 90],
    31: ["Frank Castle", "19/11/25", "22/11/2025", 93],
}


# TREEVIEW FUNCT (ctk frame as parameter )
def tree_init(parent_frame):
    dict_emp = load_embeddings()

    tree = ttk.Treeview(parent_frame, columns=("Name", "Date Start", "Date End", "Days Left"), show="headings")

    tree.heading("Name", text="Name")
    tree.heading("Date Start", text="Date Start")
    tree.heading("Date End", text="Date End")
    tree.heading("Days Left", text="Days Left")

    tree.column("Name", width=100)
    tree.column("Date Start", width=100)
    tree.column("Date End", width=100)
    tree.column("Days Left", width=100)

    for key, value in test_dict.items():
        tree.insert("", "end", values=(value[0], value[1], value[2], value[3]))

    tree.place(x=30, y=60, width=400, height=200)

    

# FILE IMPORT FUNCTION
def import_images(name, surname, data_folder, fp):
    file_path = fp  # Open file explorer -> get image path

    if file_path and file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        _, ext = os.path.splitext(file_path)  # Get original file extension (e.g., .jpg, .png)
        new_file_name = f"{name}_{surname}{ext}"  # Construct new file name: NameSurname.extension
        target_path = os.path.join(data_folder, new_file_name)  # Final destination path

        print("Final file path = ", target_path)  # DEBUG: Print path for verification

        try:
            shutil.copy(file_path, target_path)  # Copy file to data folder with new name
            return new_file_name
        except Exception as e:
            messagebox.showinfo("Error", f"Error encountered: {e}")
    else:
        messagebox.showinfo("Error", "Wrong File Format")

def reset_app():
    print("reset")
    
def del_emp():
    print("Delete emp")
    