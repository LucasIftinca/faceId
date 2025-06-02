import os
import sys

import customtkinter as ctk
from tkcalendar import Calendar
from datetime import date, timedelta, datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from .utils_gui import *
from src.face_recognition_utils.face_detection import face_detection


data_folder = r"data/images"

###########
####APP####
###########  
#==================================================================================================================================#   
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Face Recognition")
        self.geometry("460x320")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.calendar = None
        self.select_date_button = None

        # Setup main container
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize frames
        self.frames = {}
        self.frames["main"] = ctk.CTkFrame(self.container)
        self.frames["register"] = ctk.CTkFrame(self.container)
        self.frames["delete"] = ctk.CTkFrame(self.container)
        self.frames["login"] = ctk.CTkFrame(self.container)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        # Build the frames
        self.build_main_frame()
        self.build_register_frame()
        self.build_delete_frame()
        self.build_login_frame()

        # Show main frame
        self.show_frame("main")
#==================================================================================================================================#    

###################
####MAIIN FRAME####
###################   
#==================================================================================================================================#    
    def build_main_frame(self):
        frame = self.frames["main"]

        #FRAME VARIBLES#
        # frame_name = "main"

        #FRAME WIDGETS#
        button_add = ctk.CTkButton(frame, text="Add", command=lambda: self.login_frame_builder("register"), width=140, height=28)
        button_add.place(x=20, y=100)

        # button_add = ctk.CTkButton(frame, text="Add", command=self.main_frame_button_add_event, width=140, height=28)
        # button_add.place(x=20, y=100)

        button_delete = ctk.CTkButton(frame, text="Delete", command=lambda : self.login_frame_builder("delete"), width=140, height=28)
        button_delete.place(x=20, y=140)

        button_reset = ctk.CTkButton(frame, text="Reset", command=self.reset_app, width=140, height=28)
        button_reset.place(x=20, y=180)

        self.video_label = ctk.CTkLabel(frame, text="", width=300, height=240)
        self.video_label.place(x=180, y=20)

        #FUNCTIONS#
        face_detection(self.video_label)
#==================================================================================================================================#    

###################
###REGISTER FRAME##
###################   
#==================================================================================================================================#    
    def build_register_frame(self):
        frame = self.frames["register"]
        self.check_var = ctk.StringVar(value="off")

        #FRAME VARIABLES#
        today = date.today()
        tomorrow = today + timedelta(days=1)

        #FRAME WIDGETS#
        self.image_txtbox = ctk.CTkTextbox(frame, width=140, height=28)
        self.image_txtbox.place(x=20, y=100)
        self.image_txtbox.insert("1.0", "Imagine")

        self.name_txtbox = ctk.CTkTextbox(frame, width=140, height=28)
        self.name_txtbox.place(x=20, y=140)
        self.name_txtbox.insert("1.0", "Nume")

        self.datestart_txtbox = ctk.CTkTextbox(frame, width=60, height=28)
        self.datestart_txtbox.place(x=20, y=180)
        self.datestart_txtbox.insert("1.0", today.strftime("%d/%m"))
        self.datestart_txtbox.bind("<Button-1>", self.show_calendar_inline_start)

        self.datestop_txtbox = ctk.CTkTextbox(frame, width=60, height=28)
        self.datestop_txtbox.place(x=100, y=180)
        self.datestop_txtbox.insert("1.0", tomorrow.strftime("%d/%m"))
        self.datestop_txtbox.bind("<Button-1>", self.show_calendar_inline_stop)

        self.checkbox = ctk.CTkCheckBox(frame, text="Unlimited Period", command=self.reg_frame_checkbox,
                                        variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.place(x=20, y=220)

        #BUTTONS#
        button_add = ctk.CTkButton(frame, text="Add Employee", command=self.reg_frame_button_add_event, width=140, height=28)
        button_add.place(x=20, y=260)

        button_select_photo = ctk.CTkButton(frame, text="Select Photo", command=self.reg_frame_select_event, width=140, height=28)
        button_select_photo.place(x=20, y=60)
 #==================================================================================================================================#           

###################
####DELETE FRAME###
###################   
#==================================================================================================================================#      
    def build_delete_frame(self):
        frame = self.frames["delete"]
        self.check_var = ctk.StringVar(value="off")

        button_delete = ctk.CTkButton(frame, text="Delete", command=self.delete_emp, width=140, height=28)
        button_delete.place(x=30, y=270)

        button_back = ctk.CTkButton(frame, text="Back", command=self.return_to_main_frame, width=140, height=28)
        button_back.place(x = 190, y = 270)
        tree_init(frame)

###################
####LOGIN FRAME####
###################   
#==================================================================================================================================#    
    def build_login_frame(self):
        frame = self.frames["login"]

        self.username_label = ctk.CTkLabel(frame, text="User:")
        self.username_label.pack(pady=(20, 5))
        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Enter username")
        self.username_entry.pack()

        self.password_label = ctk.CTkLabel(frame, text="Password:")
        self.password_label.pack(pady=(10, 5))
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Enter password", show="*")
        self.password_entry.pack()

        self.error_label = ctk.CTkLabel(frame, text="Login Failed! Try again!", text_color="red")

        self.verify_button = ctk.CTkButton(frame, text="Verify", command=self.get_credentials)
        self.verify_button.pack(pady=20)
        
    def login_frame_builder(self, name):
        self.post_login_target = name
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.error_label.pack_forget()
        self.show_frame("login")

    def get_credentials(self):
        user = self.username_entry.get()
        password = self.password_entry.get()

        if user == "1" and password == "1":
            self.show_frame(self.post_login_target)
        else:
            self.error_label.pack(pady=(5, 0))
            self.error_label.after(2000, self.error_label.pack_forget)
################
####CALENDAR####
################ 
#==================================================================================================================================#
    def show_calendar_inline_start(self, event=None):
        frame = self.frames["register"]

        if self.calendar and self.calendar.winfo_exists():
            self.calendar.destroy()
        if self.select_date_button and self.select_date_button.winfo_exists():
            self.select_date_button.destroy()

        self.calendar = Calendar(frame, selectmode="day")
        self.calendar.place(x=200, y=60)

        self.select_date_button = ctk.CTkButton(frame, text="Use Selected Date", command=self.use_selected_date_start)
        self.select_date_button.place(x=200, y=230)

    def use_selected_date_start(self):
        raw_date = self.calendar.get_date()  # e.g., '5/7/25'
        date_selected = datetime.strptime(raw_date, "%m/%d/%y")
        formatted_date = date_selected.strftime("%d/%m")
        self.datestart_txtbox.delete("1.0", "end")
        self.datestart_txtbox.insert("1.0", formatted_date)
        self.calendar.destroy()
        self.select_date_button.destroy()

    def use_selected_date_stop(self):
        raw_date = self.calendar.get_date()  # e.g., '5/7/25'
        date_selected = datetime.strptime(raw_date, "%m/%d/%y")
        formatted_date = date_selected.strftime("%d/%m")
        self.datestop_txtbox.delete("1.0", "end")
        self.datestop_txtbox.insert("1.0", formatted_date)
        self.calendar.destroy()
        self.select_date_button.destroy()

    def show_calendar_inline_stop(self, event=None):
        frame = self.frames["register"]

        if self.calendar and self.calendar.winfo_exists():
            self.calendar.destroy()
        if self.select_date_button and self.select_date_button.winfo_exists():
            self.select_date_button.destroy()

        self.calendar = Calendar(frame, selectmode="day")
        self.calendar.place(x=200, y=60)

        self.select_date_button = ctk.CTkButton(frame, text="Use Selected Date", command=self.use_selected_date_stop)
        self.select_date_button.place(x=200, y=230)
#==================================================================================================================================#

################
####FUNCTIONS###
################      
#==================================================================================================================================#   
    def return_to_main_frame(self):
        self.show_frame("main")

    def main_frame_button_add_event(self):
        self.show_frame("register")

    def main_frame_button_delete_event(self):
        self.show_frame("delete")

    # def main_frame_button_reset_event(self):
    #     reset_app()

    def reset_app(self):
        print("RESET")

    

    def reg_frame_button_add_event(self):
        ##import_images(data_folder, name, date_start, date_stop, unlimited)
        print("NEED DICT IMPLEMENTATION")

    def reg_frame_select_event(self):
        import_images(data_folder)  # ADD PARAMETERS LATER -> name, date_start, date_stop, unlimited)

    def reg_frame_checkbox(self):
        self.show_frame("main")

    def button_delete_event(self):
        self.show_frame("delete")

    def reg_frame_login_frame(self):
        self.show_frame("login")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def delete_emp(self):
        del_emp()
#==================================================================================================================================#


################
####INNIT APP###
################  
#==================================================================================================================================#
app = App()
app.mainloop()
#==================================================================================================================================#
