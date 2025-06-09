import os
import cv2
import time
import threading
import numpy as np
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, PhotoImage
import glob
from datetime import datetime

EMBEDDINGS_FILE = "faces.npy"
COSINE_THRESHOLD = 0.5

# Load models
face_detector = cv2.FaceDetectorYN_create("src/models/face_detection_yunet_2023mar.onnx", "", (0, 0))
face_detector.setScoreThreshold(0.6)
face_recognizer = cv2.FaceRecognizerSF_create("src/models/face_recognizer_fast.onnx", "")

# Shared state
recognition_running = False
recognition_thread = None
stop_flag = False
reference_embeddings = {} # name -> [embedding, start, end, undef]

# Variabile globale pentru a stoca datele temporare și referințe la widget-uri
temp_face_embedding = None
temp_name_entry = None
temp_start_entry = None
temp_end_entry = None
temp_undef_var = None
face_detection_status_label = None # Noul label pentru statusul detecției feței în Add User

# Variabilă globală pentru a stoca ultimul status afișat pe ecran
last_displayed_status_text = ""

def load_embeddings():
    global reference_embeddings
    if os.path.exists(EMBEDDINGS_FILE):
        reference_embeddings = np.load(EMBEDDINGS_FILE, allow_pickle=True).item()
    else:
        reference_embeddings = {}

def save_embeddings():
    np.save(EMBEDDINGS_FILE, reference_embeddings)

def update_status(text, color):
    global last_displayed_status_text
    # Actualizăm label-ul de stare doar dacă textul s-a schimbat
    if text != last_displayed_status_text:
        status_label.config(text=text, fg=color)
        last_displayed_status_text = text

def recognize_loop():
    global stop_flag, last_displayed_status_text
    url_droid = "url = http//:192.168.1.x:4747" 
    url="rtsp://admin:adminadmin1@192.168.1.108:554/cam/realmonitor?channel=1&subtype=1"
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    face_detector.setInputSize((320, 240))

    frame_counter = 0
    last_displayed_status_text = "" 

    while not stop_flag:
        ret, frame = cap.read()
        if not ret:
            root.after(0, update_status, "Camera Error", "gray")
            break

        frame = cv2.resize(frame, (320, 240))
        frame_counter += 1

        if frame_counter % 10 == 0:
            _, faces = face_detector.detect(frame)
            current_status_text = "Locked"
            current_status_color = "#e74c3c"  # Red for locked
            
            if faces is not None:
                for face in faces:
                    aligned = face_recognizer.alignCrop(frame, face)
                    feature = face_recognizer.feature(aligned)

                    for name, data in reference_embeddings.items():
                        ref_emb, start, end, undef = data 
                        score = face_recognizer.match(feature, ref_emb, cv2.FaceRecognizerSF_FR_COSINE)

                        if score >= COSINE_THRESHOLD:
                            current_status_text = f"Unlocked: {name}"
                            current_status_color = "#2ecc71"  # Green for unlocked
                            break 
                    if current_status_text.startswith("Unlocked"): 
                        break

            root.after(0, update_status, current_status_text, current_status_color)
        
        time.sleep(0.01)

    cap.release()

def start_recognition():
    global recognition_running, recognition_thread, stop_flag, last_displayed_status_text
    if not recognition_running:
        stop_flag = False
        recognition_thread = threading.Thread(target=recognize_loop, daemon=True)
        recognition_thread.start()
        recognition_running = True
    last_displayed_status_text = "" 
    update_status("System Initializing...", "#f0f0f0")

def stop_recognition():
    global recognition_running, stop_flag
    stop_flag = True
    recognition_running = False

def reset_recognition():
    stop_recognition()
    time.sleep(0.5)
    start_recognition()

def add_user():
    global temp_name_entry, temp_start_entry, temp_end_entry, temp_undef_var, temp_face_embedding, face_detection_status_label

    stop_recognition()
    clear_frame()
    update_status("Maintenance", "orange") 

    tk.Label(center_frame, text="Name:", bg="#1a1a1a", fg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(10,0))
    temp_name_entry = tk.Entry(center_frame, bg="#2a2a2a", fg="#f0f0f0", insertbackground="#f0f0f0", bd=1, relief="solid", font=("Arial", 10))
    temp_name_entry.pack(ipadx=5, ipady=3)

    tk.Label(center_frame, text="Start Date (YYYY-MM-DD):", bg="#1a1a1a", fg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(10,0))
    temp_start_entry = tk.Entry(center_frame, bg="#2a2a2a", fg="#f0f0f0", insertbackground="#f0f0f0", bd=1, relief="solid", font=("Arial", 10))
    temp_start_entry.pack(ipadx=5, ipady=3)

    tk.Label(center_frame, text="End Date (YYYY-MM-DD):", bg="#1a1a1a", fg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(10,0))
    temp_end_entry = tk.Entry(center_frame, bg="#2a2a2a", fg="#f0f0f0", insertbackground="#f0f0f0", bd=1, relief="solid", font=("Arial", 10))
    temp_end_entry.pack(ipadx=5, ipady=3)

    temp_undef_var = tk.BooleanVar()
    undef_check = tk.Checkbutton(center_frame, text="Undefined Period", variable=temp_undef_var,
                                 bg="#1a1a1a", fg="#f0f0f0", selectcolor="#2a2a2a",
                                 activebackground="#2a2a2a", activeforeground="#f0f0f0",
                                 font=("Arial", 10, "bold"), relief="flat", bd=0)
    undef_check.pack(pady=10)

    tk.Button(center_frame, text="Choose Image", command=process_chosen_image, **button_style).pack(pady=5)

    face_detection_status_label = tk.Label(center_frame, text="No image selected.", bg="#1a1a1a", fg="#f0f0f0", font=("Arial", 10, "italic"))
    face_detection_status_label.pack(pady=(0, 10))

    register_button_frame = tk.Frame(center_frame, bg="#1a1a1a")
    register_button_frame.pack(pady=10)
    
    global register_user_btn
    # Modificare aici: textul butonului
    register_user_btn = tk.Button(register_button_frame, text="Add User", command=register_user_data, **button_style)
    register_user_btn.pack(side=tk.LEFT, padx=5)
    register_user_btn.config(state=tk.DISABLED)

    tk.Button(register_button_frame, text="Cancel", command=back_to_main, **button_style).pack(side=tk.LEFT, padx=5)

def process_chosen_image():
    global temp_face_embedding, register_user_btn, face_detection_status_label

    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not filepath:
        face_detection_status_label.config(text="No image selected.", fg="#f0f0f0")
        return
    image = cv2.imread(filepath)
    if image is None:
        face_detection_status_label.config(text="Error: Could not read image.", fg="#e74c3c")
        temp_face_embedding = None
        register_user_btn.config(state=tk.DISABLED)
        return

    face_detector.setInputSize(image.shape[1::-1])
    _, faces = face_detector.detect(image)
    if faces is None or len(faces) == 0:
        face_detection_status_label.config(text="No face detected in file.", fg="#e74c3c")
        temp_face_embedding = None
        register_user_btn.config(state=tk.DISABLED)
        return

    aligned_face = face_recognizer.alignCrop(image, faces[0])
    temp_face_embedding = face_recognizer.feature(aligned_face)
    face_detection_status_label.config(text="Face detected in file.", fg="#2ecc71")
    register_user_btn.config(state=tk.NORMAL)

def register_user_data():
    global temp_face_embedding, temp_name_entry, temp_start_entry, temp_end_entry, temp_undef_var

    if temp_face_embedding is None:
        messagebox.showerror("Error", "Please choose an image and detect a face first.")
        return

    name = temp_name_entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Name is required.")
        return

    start = temp_start_entry.get().strip()
    end = temp_end_entry.get().strip()
    undef = temp_undef_var.get()

    if not undef:
        try:
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            if start_date > end_date:
                messagebox.showerror("Error", "Start date cannot be after end date.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

    reference_embeddings[name] = [temp_face_embedding, start, end, undef]
    save_embeddings()

    temp_face_embedding = None
    temp_name_entry = None
    temp_start_entry = None
    temp_end_entry = None
    temp_undef_var = None
    global face_detection_status_label
    if face_detection_status_label:
        face_detection_status_label.config(text="No image selected.", fg="#f0f0f0") 

    back_to_main()


def delete_user():
    stop_recognition()
    clear_frame()
    update_status("Maintenance", "orange") 

    tk.Label(center_frame, text="Select a user to delete:", bg="#1a1a1a", fg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(10,0))

    listbox = tk.Listbox(center_frame, bg="#2a2a2a", fg="#f0f0f0", selectbackground="#007bff", selectforeground="white",
                         font=("Arial", 10), bd=1, relief="solid")
    for name in reference_embeddings:
        listbox.insert(tk.END, name)
    listbox.pack(pady=5, padx=10, fill="both", expand=True)

    def confirm_delete():
        selected = listbox.curselection()
        if selected:
            name = listbox.get(selected[0])
            del reference_embeddings[name]
            save_embeddings()
            back_to_main()
        else:
            messagebox.showwarning("No Selection", "Please select a user to delete.")

    button_frame = tk.Frame(center_frame, bg="#1a1a1a")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Delete", command=confirm_delete, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancel", command=back_to_main, **button_style).pack(side=tk.LEFT, padx=5)


def clear_frame():
    for widget in center_frame.winfo_children():
        widget.destroy()

def back_to_main():
    global temp_face_embedding, temp_name_entry, temp_start_entry, temp_end_entry, temp_undef_var, face_detection_status_label, last_displayed_status_text
    temp_face_embedding = None
    temp_name_entry = None
    temp_start_entry = None
    temp_end_entry = None
    temp_undef_var = None
    face_detection_status_label = None 

    clear_frame()
    
    # Plasează status_label în partea de sus a center_frame
    status_label.pack_forget() 
    status_label.pack(pady=(10, 20)) 

    # Creează un frame pentru butoanele principale și plasează-l sub status_label
    main_buttons_frame = tk.Frame(center_frame, bg="#1a1a1a")
    main_buttons_frame.pack(pady=10) 

    tk.Button(main_buttons_frame, text="Add User", command=add_user, **button_style).pack(fill='x', pady=5)
    tk.Button(main_buttons_frame, text="Delete User", command=delete_user, **button_style).pack(fill='x', pady=5)
    tk.Button(main_buttons_frame, text="Reset Recognition", command=reset_recognition, **button_style).pack(fill='x', pady=5)
    
    start_recognition()

# GUI Setup
root = tk.Tk()
root.title("Access Control System")
root.geometry("700x500") # Dimensiune MĂRITĂ aici
root.configure(bg="#1a1a1a")

button_style = {
    "bg": "#007bff",
    "fg": "white",
    "font": ("Arial", 12, "bold"),
    "relief": "flat",
    "borderwidth": 0,
    "highlightthickness": 0,
    "activebackground": "#0056b3",
    "activeforeground": "white",
    "padx": 10,
    "pady": 5,
}

status_label = tk.Label(root, text="System Initializing...", font=("Arial", 20, "bold"), fg="#f0f0f0", bg="#1a1a1a")

center_frame = tk.Frame(root, bg="#1a1a1a")
center_frame.pack(expand=True, fill="both", padx=20, pady=10)

load_embeddings()
back_to_main()
root.mainloop()