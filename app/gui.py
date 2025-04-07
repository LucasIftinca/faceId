import os
import shutil
import tkinter
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import customtkinter

# PATHS & GLOBAL VARIABLES
data_folder = r"datadata/images"

# SYSTEM SETTINGS
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

# APP FRAME
def init_app():
  frame = customtkinter.CTk()
  frame.geometry("460x320")                                                                   # Set width and height
  frame.title("Face Recognition")                                                             # Titlebar name
  frame.resizable(False, False)                                                               # Set resizable width = False & height = False, to keep window a predetermined size

  # WIDGETS CONTROL

  # Open File Explorer button (frame = current window)
  button_file_explore = customtkinter.CTkButton(frame, text="Add New Employee", command=button_file_explore_event, width=140, height=28)
  button_file_explore.place(x=160, y=99)                                                      # Place button at x = 160, y = 99

  # Open Employee List button
  button_emp_list = customtkinter.CTkButton(frame, text="Open Employee List", command=button_emp_list_event, width=140, height=28)
  button_emp_list.place(x=160, y=146)                                                         # Place button at x = 160, y = 146

 # Open Employee List button
  button_emp_list = customtkinter.CTkButton(frame, text="Add New Employee", command=button_emp_list_event, width=140, height=28)
  button_emp_list.place(x=160, y=146)                                                         # Place button at x = 160, y = 146

  frame.mainloop()                                                                            # Mainloop, calls app to start

# WIDGET LISTENERS
def button_file_explore_event():                                                              # Click button event -> opens File Explorer to select an image
  file_path = askopenfilename()                                                               # Open file explorer -> get image path

  if file_path and file_path.lower().endswith((".png", ".jpg", ".jpeg")):                     # Check if path is correct and image has correct extension
    file_name    = os.path.basename(file_path)                                                # Extract file name
    target_path  = os.path.join(data_folder, file_name)                                       # Build destination path by joining the data_folder (folder containg the images to be used for embedings) with the file name
    print("Final file path = ", target_path)                                                  # TEST to see final file path in data dir
    
    try: 
      shutil.move(file_path, target_path)                                                     # Move file to data folder (folder containg the images to be used for embedings) 
    except Exception as e:
        messagebox.showinfo("Error", f"Error ecountered : {e}")                               # Print error 
  else:
    messagebox.showinfo("Error", "Wrong File Format")                                         # Show error message inside Message Box



# Button: Open Employee List
def button_emp_list_event():
  print("Employee List")

# Button: Add Employee (not used yet)
def button_add_emp_event():
  print("Add Employee")

# FUNCTION CALLERS
init_app()                                                                                     # Call init_app function
