import cv2 
import tkinter as tk
from tkinter import messagebox, ttk

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.config import * 
from src.face_recog_detect import *
from src.user_management import *

#Variables 
# Tkinter window setup
root = tk.Tk()
root.title("Nokia Garage Access")
root.geometry("700x420")
root.resizable(False, False)

video_label = None
status_label = None
# Main frame
main_frame = tk.Frame(root, bg="#2b2b2b")
main_frame.pack(fill="both", expand=True)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)


def clear_frame(frame):
    # Iterăm prin copii, dar NU distrugem video_label
    for widget in frame.winfo_children():
        if widget != video_label: # Asigură-te că nu distrugi video_label
            widget.destroy()
    if video_label:
        video_label.pack_forget()


            

    
def build_video_frame(frame):
    clear_frame(frame)
    
    video_label = tk.Label(frame, bg="#e74c3c")
    height = INPUT_HEIGHT
    width = INPUT_WIDTH
    video_label.place(relx=0.5, rely=0.35, anchor="center", height=height, width=width)


    status_label = tk.Label(frame, text="Locked", **LABEL_STYLE_STATUS)
    status_label.place(relx=0.4, rely=0.7)

    button_admin_settings = tk.Button(frame, text="Admin Settings", command=lambda: build_login_frame(frame), **BUTTON_STYLE)
    button_admin_settings.place(relx=0.3, rely=0.95, anchor="s")

    button_start_recog = tk.Button(
        frame, 
        text="Start Recognition", 
        command=lambda: start_recognition(frame, video_label,status_label),
        **BUTTON_STYLE
    )
    button_start_recog.place(relx=0.7, rely=0.95, anchor="s")


def build_admin_frame(frame):
    #stop_recognition(frame, video_label)
    clear_frame(frame)

    button_add_new_emp = tk.Button(frame, text="Add Employee", command=lambda: build_add_emp_frame(frame), **BUTTON_STYLE)
    button_add_new_emp.pack(pady=20)

    button_delete_emp = tk.Button(frame, text="Delete Employee", command=lambda: build_delete_emp_frame(frame), **BUTTON_STYLE)
    button_delete_emp.pack(pady=20)

    button_reset_recog = tk.Button(frame, text="Reset Recognition", command=lambda: reset_recognition(frame, video_label, status_label), **BUTTON_STYLE)
    button_reset_recog.pack(pady=20)

    button_reset_pass = tk.Button(frame, text="Reset Password", command=lambda: build_reset_pass_frame(frame), **BUTTON_STYLE)
    button_reset_pass.pack(pady=20)


def build_login_frame(frame):
    stop_recognition(video_label)
    clear_frame(frame)
    
    container = tk.Frame(frame, bg= "#2b2b2b")
    container.place(relx=0.5, rely=0.5, anchor="center")  #REMOVE IF TOO LAGGY
    
    label_user = tk.Label(container, text="User", **LABEL_STYLE_MISC)
    label_user.pack(anchor="w", pady=2)

    entry_user = tk.Entry(container, ENTRY_STYLE)
    entry_user.pack(anchor="center", pady=2, side="top")

    label_pass = tk.Label(container, text="Password", **LABEL_STYLE_MISC)
    label_pass.pack(anchor="w", pady=2)
    
    entry_password = tk.Entry(container,ENTRY_STYLE)
    entry_password.pack(anchor="center", pady=2, side="top")
    
    label_result  = tk.Label(frame, text="Login Failed! Try again!", foreground ="#ff0000")
    
    
    def verify_credentials():
        username = entry_user.get()
        password = entry_password.get()
        logged_in = (username == "1" and password == "1")  # example

        
        
        if logged_in:
            build_admin_frame(frame)
            # add other frames as needed
        else:
            label_result.pack(pady= 10)
            label_result.after(2000, label_result.pack_forget)
            
    button_confirm = tk.Button(container, text = "Login", command= lambda : verify_credentials(), **BUTTON_STYLE )
    button_confirm.pack(anchor= "center", pady= 10)


def build_add_emp_frame(frame):
    data_holder = {"embedding": None}  # Use a mutable dict to store the embedding
    
    
    clear_frame(frame)

    container = tk.Frame(frame, bg= "#2b2b2b")
    container.place(relx=0.25, rely=0.5, anchor="center")  #REMOVE IF TOO LAGGY

    label_name = tk.Label(container, text="Name", **LABEL_STYLE_MISC)
    label_name.pack(anchor="w", pady=2)
    
    entry_name = tk.Entry(container, ENTRY_STYLE ) #width= 19)
    entry_name.pack(anchor="center", pady=2)


    label_date_start = tk.Label(container, text="Start Date",  **LABEL_STYLE_MISC)
    label_date_start.pack(anchor="w", pady=2)
    
    entry_date_start = tk.Entry(container, ENTRY_STYLE )
    entry_date_start.pack(anchor="center", pady=2)


    label_date_stop = tk.Label(container, text="End Date",  **LABEL_STYLE_MISC)
    label_date_stop.pack(anchor="w", pady=2)
    
    entry_date_stop = tk.Entry(container, ENTRY_STYLE )
    entry_date_stop.pack(anchor="center", pady=2)


    temp_undef_var = tk.BooleanVar()
    undef_check = tk.Checkbutton(container, text="Undefined Period ", variable=temp_undef_var,
                                 bg="#2b2b2b", fg="#FFFFFF", selectcolor="#007bff",
                                 activebackground="#007bff", activeforeground="#FFFFFF",
                                 font=("Roboto", 10), relief="flat", bd=0)
    undef_check.pack(anchor="center", pady=3)
    
    label_valid_image = tk.Label(container, text="Valid image here", **LABEL_STYLE_STATUS)
    label_valid_image.pack(anchor="center", pady=3)
    
    
    button_add_emp_data = tk.Button(container, text = "Add Employee", command=lambda: register_emp_data(entry_name, entry_date_start, entry_date_stop, temp_undef_var,  data_holder["embedding"]), **BUTTON_STYLE)
    button_add_emp_data.config(state= tk.DISABLED)
    
    button_import_images = tk.Button(container, text = "Import Image", command= lambda : process_chosen_image(label_valid_image, button_add_emp_data, data_holder), **BUTTON_STYLE)
    button_import_images.pack(anchor="center", pady=5)
    
   
    button_add_emp_data.pack(anchor="center", pady=3)
    
    button_back_to_video = tk.Button(frame, text="Back", command=lambda: build_video_frame(frame), **BUTTON_STYLE)
    button_back_to_video.pack(anchor="e", pady=5)


   
    
def build_delete_emp_frame(frame):
    clear_frame(frame)
    columns = ("Name", "Start Date", "End Date", "Unlimited")
    
    # Mutable container to hold the selected name
    selected_name = [None]  
    
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    embeddings_dict = load_embeddings()
    for name, (embedding, start, end, undef) in embeddings_dict.items():
        tree.insert("", tk.END, values=(name, start, end, undef))

    tree.pack(padx=10, pady=10, fill='x', expand=True, anchor="n")
    
    # Create delete button, initially disabled
    button_delete_emp = tk.Button(frame, text="Delete Selected", command=lambda: delete_emp(tree, button_delete_emp), state=tk.DISABLED, **BUTTON_STYLE)
    button_delete_emp.pack(side=tk.LEFT, padx=5, pady=10)

    button_back_to_video = tk.Button(frame, text="Back", command=lambda: build_video_frame(frame), **BUTTON_STYLE)
    button_back_to_video.pack(side=tk.LEFT, padx=5, pady=10)
    # Define selection handler
    
    def on_tree_select(event):
        selected_item = tree.focus()
        button_delete_emp.config(
            state=tk.NORMAL if selected_item else tk.DISABLED
        )

    tree.bind("<<TreeviewSelect>>", on_tree_select)

        
        
def build_reset_pass_frame(frame):
    print()
    
# Build UI
build_video_frame(main_frame)
#build_add_emp_frame(main_frame)
#build_admin_frame(main_frame)
#build_delete_emp_frame(main_frame)


# Run app
root.mainloop()