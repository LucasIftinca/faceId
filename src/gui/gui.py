import os
import sys
import threading
import cv2

import customtkinter as ctk
from tkcalendar import Calendar
from customtkinter import CTkImage
from PIL import Image, ImageTk
from datetime import date, timedelta, datetime
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from .utils_gui import *
from src.face_recognition_utils.face_detection import *
from src.face_recognition_utils.face_recognition import *
from src.face_recognition_utils.model_loader import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMAGES_DIR = os.path.join(BASE_DIR, "data", "images")

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
        
        button_delete = ctk.CTkButton(frame, text="Delete", command=lambda : self.login_frame_builder("delete"), width=140, height=28)
        button_delete.place(x=20, y=140)

        # button_reset = ctk.CTkButton(frame, text="Reset", command=self.reset_app, width=140, height=28)
        # button_reset.place(x=20, y=180)

        self.video_label = ctk.CTkLabel(frame, text="", width=300, height=240)
        self.video_label.place(x=180, y=20)

        #FUNCTIONS#
        #face_detection(self.video_label)
        threading.Thread(target=self.run_face_detection_thread, daemon=True).start()
        
#==================================================================================================================================#    

###################
###REGISTER FRAME##
###################   
#==================================================================================================================================#    
    def build_register_frame(self):
        frame = self.frames["register"]
        self.check_var = ctk.StringVar(value="False")

        #FRAME VARIABLES#
        today = date.today()
        tomorrow = today + timedelta(days=1)

 #FRAME VARIABLES#
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        # button_select_photo = ctk.CTkButton(frame, text="SPhotoelect ", command=self.get_filepath, width=140, height=28)
        # button_select_photo.place(x=20, y=15)
        
        # button_select_photo = ctk.CTkButton(frame, text="DELET MAIN FRAME ", command=self.import_images, width=140, height=28)
        # button_select_photo.place(x=20, y=15)

        # Name Label + Entry
        self.name_label = ctk.CTkLabel(frame, text="Name:")
        self.name_label.place(x=20, y=45)

        self.name_txtbox = ctk.CTkEntry(frame, width=140, height=28)
        self.name_txtbox.place(x=20, y=75)

        # Surname Label + Entry
        self.surname_label = ctk.CTkLabel(frame, text="Surname:")
        self.surname_label.place(x=20, y=105)

        self.surname_txtbox = ctk.CTkEntry(frame, width=140, height=28)
        self.surname_txtbox.place(x=20, y=135)

        # Start Date Label + Entry
        self.start_label = ctk.CTkLabel(frame, text="Start Date:")
        self.start_label.place(x=20, y=165)

        self.datestart_txtbox = ctk.CTkTextbox(frame, width=80, height=28)
        self.datestart_txtbox.place(x=20, y=195)
        self.datestart_txtbox.insert("1.0", today.strftime("%d/%m/%y"))
        self.datestart_txtbox.bind("<Button-1>", self.show_calendar_inline_start)

        # Stop Date Label + Entry
        self.stop_label = ctk.CTkLabel(frame, text="Stop Date:")
        self.stop_label.place(x=100, y=165)

        self.datestop_txtbox = ctk.CTkTextbox(frame, width=80, height=28)
        self.datestop_txtbox.place(x=100, y=195)
        self.datestop_txtbox.insert("1.0", tomorrow.strftime("%d/%m/%y"))
        self.datestop_txtbox.bind("<Button-1>", self.show_calendar_inline_stop)

        # Unlimited Period Checkbox
        self.unlimited = ctk.CTkCheckBox(
            frame,
            text="Unlimited Period",
            variable=self.check_var,
            onvalue="True",
            offvalue="False"
        )
        self.unlimited.place(x=20, y=230)


        #BUTTONS#
        button_add = ctk.CTkButton(frame, text="Add Employee", command=self.get_emp_info, width=140, height=28)
        button_add.place(x=20, y=265)
        
        button_add = ctk.CTkButton(frame, text="Add Employee", command=self.show_frame("main"), width=140, height=28)
        button_add.place(x=180, y=265)
        

 #==================================================================================================================================#           

###################
####DELETE FRAME###
###################   
#==================================================================================================================================#      
    def build_delete_frame(self):
        frame = self.frames["delete"]
        tree = tree_init(frame)

        button_delete = ctk.CTkButton(frame, text="Delete", command=lambda: delete_emp_from_dict(frame, tree), width=140, height=28)
        button_delete.place(x=30, y=270)

        button_back = ctk.CTkButton(frame, text="Back", command=self.show_frame("main"), width=140, height=28)
        button_back.place(x = 190, y = 270)
        
    

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
        formatted_date = date_selected.strftime("%d/%m/%y")
        self.datestart_txtbox.delete("1.0", "end")
        self.datestart_txtbox.insert("1.0", formatted_date)
        self.calendar.destroy()
        self.select_date_button.destroy()

    def use_selected_date_stop(self):
        raw_date = self.calendar.get_date()  # e.g., '5/7/25'
        date_selected = datetime.strptime(raw_date, "%m/%d/%y")
        formatted_date = date_selected.strftime("%d/%m/%y")
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
    def rebuild_main_frame(self):

        #self.frames["main"] = ctk.CTkFrame(self.container)
        self.frames["main"] = ctk.CTkFrame(self.container)
        self.frames["main"].grid(row=0, column=0, sticky="nsew")
        
        self.build_main_frame()
        self.show_frame("main")
    
    
    def main_frame_button_add_event(self):
        self.show_frame("register")

    def main_frame_button_delete_event(self):
        self.show_frame("delete")      

    def button_delete_event(self):
        self.show_frame("delete")

    def reg_frame_login_frame(self):
        self.show_frame("login")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
    
    def get_filepath(self):
        self.selected_file_path = askopenfilename()
        
    def get_emp_info(self):
        name = self.name_txtbox.get()
        surname = self.surname_txtbox.get()

        print(self.check_var.get())

        if self.check_var.get() == "True":  
            start_date_obj = datetime.today()
            stop_date_obj = datetime.strptime("01/01/3000", "%d/%m/%Y")  # 4-digit year
            days_left = -1
        else:
            try:
                # Expecting input as dd/mm/yy (2-digit year)
                start_str = self.datestart_txtbox.get("1.0", "end").strip()
                stop_str = self.datestop_txtbox.get("1.0", "end").strip()

                start_date_obj = datetime.strptime(start_str, "%d/%m/%y")
                stop_date_obj = datetime.strptime(stop_str, "%d/%m/%y")
                days_left = (stop_date_obj - start_date_obj).days
            except ValueError:
                print("Invalid date format. Please use dd/mm/yy.")
                return  # stop execution if invalid input

        start_date = start_date_obj.strftime("%d/%m/%y")
        stop_date = stop_date_obj.strftime("%d/%m/%y")

        import_images(name, surname, data_folder, self.selected_file_path)  # ADD PARAMETERS LATER -> name, date_start, date_stop, unlimited)
        
        info = [name, surname, start_date, stop_date, days_left]
        print(info)
        
        self.show_frame("main")
    
    
    def update_video_label(self, imgtk):
        self.video_label.configure(image=imgtk)
        self.video_label.image = imgtk

   
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
        print("Deleted from tree view.")
    
    
    def run_face_detection_thread(self):
        face_detector, face_recognizer = load_models()
        embeddings = load_dictionary()

        url = "rtsp://admin:adminadmin1@192.168.1.108:554/cam/realmonitor?channel=1&subtype=1"
        capture = cv2.VideoCapture(url)

        if not capture.isOpened():
            print("EROARE CAMERA")
            return

        frame_count = 0
        while True:
            ret, frame = capture.read()
            if not ret:
                time.sleep(0.1)
                continue

            frame_count += 1
            # Only process every 5th frame for performance
            if frame_count % 5 == 0:
                processed_frame = process_frame(frame, face_detector, face_recognizer, embeddings)
            else:
                processed_frame = frame

            display_frame = cv2.resize(processed_frame, (300, 240))
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(display_frame)
            imgtk = ImageTk.PhotoImage(img)

            def update_gui(imgtk_copy=imgtk):
                self.video_label.configure(image=imgtk_copy)
                self.video_label.image = imgtk_copy  # prevent garbage collection

            self.video_label.after(1, update_gui)

            # Sleep for ~30 FPS
            time.sleep(1 / 30)



#==================================================================================================================================#


################
####INNIT APP###
################  
#==================================================================================================================================#
app = App()
app.mainloop()
#==================================================================================================================================#
