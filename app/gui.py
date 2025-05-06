import os
import shutil
import sys 
import tkinter
from tkinter import messagebox, ttk

import customtkinter

from utils_gui import tree_init, import_images

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from main import main
#from src.utils import face_func

# PATHS & GLOBAL VARIABLES
data_folder = r"datadata/images"                                                                                  # PATH to image folder

# SYSTEM SETTINGS
customtkinter.set_appearance_mode("Dark")                                                                         # Set appearance mode to Dark
customtkinter.set_default_color_theme("blue")                                                                     # Set color theme to blue

# APP FRAME
def init_app():
    global video_label
    frame = customtkinter.CTk()
    frame.geometry("460x320")                                                                                     # Set width and height
    frame.title("Testq")                                                                               # Titlebar name
    frame.resizable(False, False)                                                                                 # Disable resizing

    # WIDGETS CONTROL
    

    # BUTTONS                                                

    button_add = customtkinter.CTkButton(frame, text="Add", command=button_add_event, width=140, height=28)      # Open Employee List button
    button_add.place(x=20, y=100)              
    
    button_delete=  customtkinter.CTkButton(frame, text="Delete", command=button_delete_event ,width=140, height=28)      # Open Employee List button
    button_delete.place(x=20, y=180)              

    button_reset=  customtkinter.CTkButton(frame, text="Reset", command=button_reset_event ,width=140, height=28)      # Open Employee List button
    button_reset.place(x=20, y=140)              
   
    video_label = customtkinter.CTkLabel(frame, text="", width=260, height=200)
    video_label.place(x=180, y=20)
    #tree_init(frame)                                                                                                 # Initialize the Treeview

    frame.mainloop()                                                                                                 # Start app main loop

# WIDGET LISTENERS
def button_add_event():                                                                                   # File Explorer button click
    import_images(data_folder)                                                                                     # Import image file to folder

def button_delete_event():                                                                                       # Employee List button click
    main(video_label)                                                                                        # Placeholder print

def button_reset_event():                                                                                        # Add Employee button click
    print("Add Employee")                                                                                          # Placeholder print

# FUNCTION CALLERS
                                                                                                          # Call init_app function
init_app()
#face_func()