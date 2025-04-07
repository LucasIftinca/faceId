import os
import shutil

import tkinter
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename

import customtkinter

test_dict = {
    1: ["Alice", "2025-04-07", 95],
    2: ["Bob", "2025-04-06", 88],
    3: ["Charlie", "2025-04-05", 92]
}

# TREEVIEW FUNCT (ctk frame as parameter )
def tree_init(parent_frame):
    tree = ttk.Treeview(parent_frame, columns=("Name", "Date", "Time"), show="headings")         # Choose CTk frame to display in (it's passed from gui.py) | Add column headers
    tree.heading("Name", text="Name")                                                            # Set header for 'Name' column
    tree.heading("Date", text="Date")                                                            # Set header for 'Date' column
    tree.heading("Time", text="Time")                                                            # Set header for 'Time' column

    tree.column("Name", width=133)                                                               # Set width for 'Name' column
    tree.column("Date", width=133)                                                               # Set width for 'Date' column
    tree.column("Time", width=133)                                                               # Set width for 'Time' column
    
    for key, value in test_dict.items():                                                         # Iterate through test_dict and insert each entry
        tree.insert("", "end", values=(value[0], value[1], value[2]))                            # Insert row with name, date, score
    
    tree.place(x=50, y=50, width=400, height=200)                                                # Place the Treeview at given coordinates with size

# FILE IMPORT FUNCTION
def import_images(data_folder):
    file_path = askopenfilename()                                                                # Open file explorer -> get image path

    if file_path and file_path.lower().endswith((".png", ".jpg", ".jpeg")):                      # Check if path is correct and image has correct extension
        file_name   = os.path.basename(file_path)                                                # Extract file name from path
        target_path = os.path.join(data_folder, file_name)                                       # Build full destination path in data folder
        print("Final file path = ", target_path)                                                 # DEBUG: Print the destination path for verification
        
        try: 
            shutil.move(file_path, target_path)                                                  # Move file to data folder (for embeddings)
        
        except Exception as e:
            messagebox.showinfo("Error", f"Error encountered : {e}")                             # Show error message if file move fails
    else:
        messagebox.showinfo("Error", "Wrong File Format")                                        # Show error message for invalid file type


