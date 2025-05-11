import os
import sys
import customtkinter
from tkcalendar import Calendar
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils_gui import *
from main import main

###########################
# PATHS & GLOBAL VARIABLES #
###########################

data_folder = os.path.join("data", "images")  # Adjusted path to look more standard
video_label = None
image_path_txtbox = None

####################
# SYSTEM SETTINGS  #
####################
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

####################
# APP AND CONTAINER #
####################
main_app = customtkinter.CTk()
main_app.geometry("460x320")
main_app.title("Face Recognition")
main_app.resizable(False, False)

container = customtkinter.CTkFrame(main_app)
container.pack(fill = "both", expand=True)

container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

frames = {}

main_frame = customtkinter.CTkFrame(container)
reg_frame = customtkinter.CTkFrame(container)

for frame in (main_frame, reg_frame):
    frame.grid(row=0, column=0, sticky="nsew")

frames["main"] = main_frame
frames["register"] = reg_frame

####################
# FUNCTION HELPERS #
####################
def show_frame(name):
    frame = frames[name]
    frame.tkraise()

def button_add_event():
    show_frame("register")

def button_delete_event():
    print("Delete button clicked")  # Placeholder

def button_reset_event():
    print("Reset button clicked")  # Placeholder
    
def reg_frame_add_emp():
    global image_path_txtbox
    filename = import_images(data_folder)
    print(filename)
    text_filename = filename
   
def reg_frame_checkbox():
    #reg_frame.destroy()
    show_frame("main")

####################
# BUILD MAIN FRAME #
####################
def build_main_frame():
    global video_label

    button_add = customtkinter.CTkButton(main_frame, text="Add", command=button_add_event, width=140, height=28)
    button_add.place(x=20, y=100)

    button_reset = customtkinter.CTkButton(main_frame, text="Reset", command=button_reset_event, width=140, height=28)
    button_reset.place(x=20, y=140)

    button_delete = customtkinter.CTkButton(main_frame, text="Delete", command=button_delete_event, width=140, height=28)
    button_delete.place(x=20, y=180)

    video_label = customtkinter.CTkLabel(main_frame, text="", width=180, height=180)
    video_label.place(x=180, y=20)

    # Run your main face recognition function (assumes it updates video_label)
    main(video_label)

########################
# BUILD REGISTER FRAME #
########################
def build_reg_frame():
    
    check_var = customtkinter.StringVar(value="off")

    #label = customtkinter.CTkLabel(reg_frame, text="Register Page")
    #label.place(x=150, y=120)

    #button_back = customtkinter.CTkButton(reg_frame, text="Back", command=lambda: show_frame("main"))
    #button_back.place(x=150, y=160)
    
    button_select_photo = customtkinter.CTkButton(reg_frame, text="Select Photo", command=reg_frame_add_emp, width=140, height=28)
    button_select_photo.place(x=20, y=60)
    
    image_txtbox = customtkinter.CTkTextbox(reg_frame, width= 140, height= 28)
    image_txtbox.place(x = 20, y = 100)
    
    name_txtbox = customtkinter.CTkTextbox(reg_frame, width= 140, height= 28)
    name_txtbox.place(x = 20, y = 140)
    
    image_txtbox = customtkinter.CTkTextbox(reg_frame, width= 60, height= 28)
    image_txtbox.place(x = 100, y = 180)
    
    image_txtbox = customtkinter.CTkTextbox(reg_frame, width= 60, height= 28)
    image_txtbox.place(x = 20, y = 180)
    image_txtbox.configure(state="disabled")
    #image_txtbox.insert("0.0",text_filename)
    
    checkbox = customtkinter.CTkCheckBox(reg_frame, text="Unlimited Period", command=reg_frame_checkbox,
                                     variable=check_var, onvalue="on", offvalue="off")
    checkbox.place(x=20, y = 220)
    
    button_add = customtkinter.CTkButton(reg_frame, text="Add Employee", command=button_add_event, width=140, height=28)
    button_add.place(x=20, y=260)
    
    calendar = Calendar(reg_frame, selectmode = "day")
    calendar.place(x = 200, y = 60)
    

####################
# INITIALIZATION   #
####################
build_main_frame()
build_reg_frame()

show_frame("main")
main_app.mainloop()
