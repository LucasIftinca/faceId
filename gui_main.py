import os
import cv2
import time
import threading
import numpy as np
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, PhotoImage
from PIL import Image, ImageTk 
import glob
from datetime import datetime

EMBEDDINGS_FILE = "faces.npy"
COSINE_THRESHOLD = 0.5

# Load models
face_detector = cv2.FaceDetectorYN_create("face_detection_yunet_2023mar.onnx", "", (0, 0))
face_detector.setScoreThreshold(0.6)
face_recognizer = cv2.FaceRecognizerSF_create("face_recognizer_fast.onnx", "")

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
face_detection_status_label = None 

# Variabilă globală pentru a stoca ultimul status afișat pe ecran
last_displayed_status_text = ""

# Variabile globale pentru video stream și display
video_label = None # Acesta va fi creat o singură dată
cap = None 

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
    if text != last_displayed_status_text:
        status_label.config(text=text, fg=color)
        last_displayed_status_text = text

def recognize_loop():
    global stop_flag, last_displayed_status_text, cap, video_label

    url = r"http://192.168.1.133:4747/video" 
    cap = cv2.VideoCapture(0)
    
    input_width, input_height = 160, 140
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, input_width)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, input_height)
    face_detector.setInputSize((input_width, input_height))

    frame_counter = 0
    last_displayed_status_text = "" 

    while not stop_flag:
        ret, frame = cap.read()
        if not ret:
            root.after(0, update_status, "Camera Error", "gray")
            # Adăugăm un mesaj de eroare vizual pe label-ul video
            if video_label and not stop_flag: # Nu afișa eroare dacă thread-ul se oprește oricum
                blank_img = np.zeros((input_height, input_width, 3), dtype=np.uint8)
                cv2.putText(blank_img, "Camera Error", (50, input_height // 2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                img = Image.fromarray(blank_img)
                imgtk = ImageTk.PhotoImage(image=img)
                video_label.imgtk = imgtk
                video_label.config(image=imgtk)
            time.sleep(1) # Așteaptă înainte de a reîncerca
            continue # Treci la următoarea iterație pentru a reîncerca
            # break # Nu mai dăm break, ci încercăm continuu să deschidem camera

        frame_display = cv2.resize(frame, (input_width, input_height))
        frame_process = frame_display.copy()

        frame_counter += 1

        if frame_counter % 10 == 0:
            _, faces = face_detector.detect(frame_process)
            current_status_text = "Locked"
            current_status_color = "#e74c3c"  
            
            if faces is not None and len(faces) > 0:
                faces_np = np.array(faces)
                valid_faces = faces_np[np.where((faces_np[:, 2] > 0) & (faces_np[:, 3] > 0))]
                
                if len(valid_faces) > 0:
                    areas = valid_faces[:, 2] * valid_faces[:, 3]
                    sorted_indices = np.argsort(areas)[::-1]
                    largest_face = valid_faces[sorted_indices[0]]

                    x, y, w, h = int(largest_face[0]), int(largest_face[1]), int(largest_face[2]), int(largest_face[3])
                    cv2.rectangle(frame_display, (x, y), (x + w, y + h), (0, 255, 0), 2) # Verde

                    aligned = face_recognizer.alignCrop(frame_process, largest_face)
                    feature = face_recognizer.feature(aligned)

                    for name, data in reference_embeddings.items():
                        ref_emb, start, end, undef = data 
                        score = face_recognizer.match(feature, ref_emb, cv2.FaceRecognizerSF_FR_COSINE)

                        if score >= COSINE_THRESHOLD:
                            current_status_text = f"Unlocked: {name}"
                            current_status_color = "#2ecc71"  
                            break 
            
            root.after(0, update_status, current_status_text, current_status_color)
        
        img = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Aceasta linie este crucială și trebuie să se afle în thread-ul principal Tkinter.
        # Din moment ce suntem într-un thread separat, folosim root.after() pentru a programa actualizarea.
        # Acest lucru previne eroarea "invalid command name".
        if video_label and video_label.winfo_exists(): # Verifică dacă widget-ul încă există
            root.after(0, lambda: video_label.config(image=imgtk))
            root.after(0, lambda: setattr(video_label, '_imgtk', imgtk)) # Această linie asigură persistența imaginii

        time.sleep(0.01)

    if cap:
        cap.release()
    # Nu mai curățăm imaginea aici, pentru că se va face în back_to_main sau la stop
    # video_label.config(image='') # <-- LINIA ACEASTA ESTE PROBLEMATICĂ CÂND LABEL-UL ESTE DEJA DISTRUS

def start_recognition():
    global recognition_running, recognition_thread, stop_flag, last_displayed_status_text, video_label
    if not recognition_running:
        stop_flag = False
        # Asigură-te că video_label este vizibil
        if video_label:
            video_label.pack(pady=10) # Re-pack pentru a fi sigur că e în layout și vizibil

        recognition_thread = threading.Thread(target=recognize_loop, daemon=True)
        recognition_thread.start()
        recognition_running = True
    last_displayed_status_text = "" 
    update_status("System Initializing...", "#f0f0f0")

def stop_recognition():
    global recognition_running, stop_flag, cap
    stop_flag = True
    recognition_running = False
    # Așteaptă puțin pentru ca thread-ul să se oprească curat
    if recognition_thread and recognition_thread.is_alive():
        recognition_thread.join(timeout=1) 
    if cap: 
        cap.release()
        cap = None 
    
    # Curățăm imaginea de pe video_label doar aici, în thread-ul principal
    if video_label and video_label.winfo_exists():
        video_label.config(image='') # Curăță imaginea, dar NU distruge widget-ul

def reset_recognition():
    stop_recognition()
    # Dă timp pentru ca thread-ul vechi să se termine complet
    # before starting a new one. This might prevent some race conditions.
    time.sleep(0.1) # Redus la 0.1s pentru a fi mai rapid, dar poți ajusta
    start_recognition()

def add_user():
    global temp_name_entry, temp_start_entry, temp_end_entry, temp_undef_var, temp_face_embedding, face_detection_status_label, video_label

    stop_recognition()
    clear_frame() # Această funcție va distruge tot CU EXCEPȚIA video_label
    update_status("Maintenance", "orange") 

    # Ascunde video_label când suntem în meniul de adăugare/ștergere utilizatori
    if video_label:
        video_label.pack_forget()

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

    img_height, img_width = image.shape[:2]
    face_detector.setInputSize((img_width, img_height)) 
    
    _, faces = face_detector.detect(image)
    if faces is None or len(faces) == 0:
        face_detection_status_label.config(text="No face detected in file.", fg="#e74c3c")
        temp_face_embedding = None
        register_user_btn.config(state=tk.DISABLED)
        return

    faces_np = np.array(faces)
    valid_faces = faces_np[np.where((faces_np[:, 2] > 0) & (faces_np[:, 3] > 0))]
    
    if len(valid_faces) > 0:
        areas = valid_faces[:, 2] * valid_faces[:, 3]
        largest_face = valid_faces[np.argsort(areas)[::-1][0]]
        
        aligned_face = face_recognizer.alignCrop(image, largest_face)
        temp_face_embedding = face_recognizer.feature(aligned_face)
        face_detection_status_label.config(text="Face detected in file.", fg="#2ecc71")
        register_user_btn.config(state=tk.NORMAL)
    else:
        face_detection_status_label.config(text="No valid face detected in file.", fg="#e74c3c")
        temp_face_embedding = None
        register_user_btn.config(state=tk.DISABLED)


def register_user_data():
    global temp_face_embedding, temp_name_entry, temp_start_entry, temp_end_entry, temp_undef_var

    if temp_face_embedding is None:
        messagebox.showerror("Error", "Please choose an image and detect a face first.")
        return

    name = temp_name_entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Name is required.")
        return
    
    if name in reference_embeddings:
        if not messagebox.askyesno("Warning", f"User '{name}' already exists. Do you want to overwrite their data?"):
            return # Nu suprascrie dacă utilizatorul anulează
        
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
            messagebox.showerror("Error", "Invalid date format. Please use %Y-%m-%d.")
            return

    reference_embeddings[name] = [temp_face_embedding, start, end, undef]
    save_embeddings()
    messagebox.showinfo("Success", f"User '{name}' added successfully.")

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
    global video_label
    stop_recognition()
    clear_frame() # Această funcție va distruge tot CU EXCEPȚIA video_label
    update_status("Maintenance", "orange") 

    if video_label:
        video_label.pack_forget()

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
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{name}'?"):
                del reference_embeddings[name]
                save_embeddings()
                messagebox.showinfo("Success", f"User '{name}' deleted successfully.")
                back_to_main()
        else:
            messagebox.showwarning("No Selection", "Please select a user to delete.")

    button_frame = tk.Frame(center_frame, bg="#1a1a1a")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Delete", command=confirm_delete, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancel", command=back_to_main, **button_style).pack(side=tk.LEFT, padx=5)


def clear_frame():
    # Iterăm prin copii, dar NU distrugem video_label
    for widget in center_frame.winfo_children():
        if widget != video_label: # Asigură-te că nu distrugi video_label
            widget.destroy()

def back_to_main():
    global temp_face_embedding, temp_name_entry, temp_start_entry, temp_end_entry, temp_undef_var, face_detection_status_label, last_displayed_status_text, video_label
    temp_face_embedding = None
    temp_name_entry = None
    temp_start_entry = None
    temp_end_entry = None
    temp_undef_var = None
    face_detection_status_label = None 

    clear_frame() # Acum clear_frame nu mai distruge video_label
    
    # Plasează status_label în partea de sus a center_frame
    status_label.pack_forget() 
    status_label.pack(pady=(10, 20)) 

    # Asigură-te că video_label este vizibil
    if video_label: # Verificăm dacă există înainte de a încerca să-l pack-uim
        video_label.pack(pady=10) 

    # Creează un frame pentru butoanele principale și plasează-l sub status_label și video_label
    main_buttons_frame = tk.Frame(center_frame, bg="#1a1a1a")
    main_buttons_frame.pack(pady=10) 

    tk.Button(main_buttons_frame, text="Add User", command=add_user, **button_style).pack(fill='x', pady=5)
    tk.Button(main_buttons_frame, text="Delete User", command=delete_user, **button_style).pack(fill='x', pady=5)
    tk.Button(main_buttons_frame, text="Reset Recognition", command=reset_recognition, **button_style).pack(fill='x', pady=5)
    
    start_recognition()

# GUI Setup
root = tk.Tk()
root.title("Access Control System")
root.geometry("700x650") 
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

# Creează video_label O SINGURĂ DATĂ la inițializarea GUI
video_label = tk.Label(center_frame, bg="#1a1a1a") 
# Nu îl pack-uim aici, îl vom pack-ui în back_to_main()

load_embeddings()
back_to_main()
root.mainloop()