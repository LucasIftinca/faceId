import os
import shutil

import tkinter
from tkinter import messagebox, ttk

import customtkinter

from utils_gui import tree_init, import_images

# PATHS & GLOBAL VARIABLES
data_folder = r"datadata/images"                                                                                  # PATH to image folder

# SYSTEM SETTINGS
customtkinter.set_appearance_mode("Dark")                                                                         # Set appearance mode to Dark
customtkinter.set_default_color_theme("blue")                                                                     # Set color theme to blue

# APP FRAME
def init_app():
    frame = customtkinter.CTk()
    frame.geometry("460x320")                                                                                     # Set width and height
    frame.title("Face Recognition")                                                                               # Titlebar name
    frame.resizable(False, False)                                                                                 # Disable resizing

    # WIDGETS CONTROL

    # BUTTONS
    button_file_explore = customtkinter.CTkButton(frame, text="Add New Employee", command=button_file_explore_event)  # Open File Explorer button
    #button_file_explore.place(x=160, y=99, width=140, height=28)                                                     # Place button

    button_emp_list = customtkinter.CTkButton(frame, text="Manage Employee List", command=button_emp_list_event)      # Open Employee List button
    #button_emp_list.place(x=160, y=146, width=140, height=28)                                                        # Place button

    button_emp_list = customtkinter.CTkButton(frame, text="Add New Employee", command=button_emp_list_event)         # Duplicate: Add New Employee
    #button_emp_list.place(x=160, y=146, width=140, height=28)                                                       # Place button

    #tree_init(frame)                                                                                                 # Initialize the Treeview

    frame.mainloop()                                                                                                 # Start app main loop

# WIDGET LISTENERS
def button_file_explore_event():                                                                                   # File Explorer button click
    import_images(data_folder)                                                                                     # Import image file to folder

def button_emp_list_event():                                                                                       # Employee List button click
    print("Employee List")                                                                                         # Placeholder print

def button_add_emp_event():                                                                                        # Add Employee button click
    print("Add Employee")                                                                                          # Placeholder print

# FUNCTION CALLERS
init_app()                                                                                                         # Call init_app function
