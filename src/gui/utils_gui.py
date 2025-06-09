import os
import shutil
import socket
import cv2
import os
import numpy as np


import tkinter
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename

from src.face_recognition_utils.model_loader import load_dictionary
from src.face_recognition_utils.face_recognition import generate_embedding

import customtkinter

# TREEVIEW FUNCT (ctk frame as parameter )
def tree_init(parent_frame):
    global dict_emp
    dict_emp = load_dictionary()

    tree = ttk.Treeview(parent_frame, columns=("Name", "Date Start", "Date End", "Days Left"), show="headings")

    tree.heading("Name", text="Name")
    tree.heading("Date Start", text="Date Start")
    tree.heading("Date End", text="Date End")
    tree.heading("Days Left", text="Days Left")

    tree.column("Name", width=100)
    tree.column("Date Start", width=100)
    tree.column("Date End", width=100)
    tree.column("Days Left", width=100)

    for key, value in dict_emp.items():
        tree.insert("", "end", iid=key, values=(value[0], value[1], value[2], value[3]))

    tree.place(x=30, y=60, width=400, height=200)
    return tree  # Return the tree for external reference (like in delete function)

def delete_emp_from_dict(frame, tree):
    item = tree.focus()
    if not item:
        print("No item selected.")
        return
    
    # Remove from dictionary
    if item in dict_emp:
        del dict_emp[item]
        print(f"Deleted {item} from dict.")

    # Remove from treeview
    tree.delete(item)
    np.save(r"data/embeddings_test.npy", dict_emp) #CHANGE PATH TO GLOBAL VARIABLE 
    print("Deleted from tree view.")
    
    

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

def add_data_dictionary(name, start_date, end_date, unlimited_period, path):
    
    #VARIABELS#
    embedding = generate_embedding(path)
    
    info_emp = [embedding, start_date, end_date, unlimited_period]
    
    data_dict = load_dictionary()
    
    data_dict[name] = info_emp
    
    np.save(r"data/embeddings_test.npy", data_dict) #CHANGE PATH TO GLOBAL VARIABLE 

def delete_data_dictionary(name, old_dict):
    del old_dict["name"]
    
   
    