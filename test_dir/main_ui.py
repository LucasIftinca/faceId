import os
import cv2
import time
import threading
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime


class AccessControlApp:
    EMBEDDINGS_FILE = "data/faces.npy"
    COSINE_THRESHOLD = 0.5

    def __init__(self, root):
        self.root = root
        self.root.title("Access Control System")
        self.root.geometry("700x500")
        self.root.configure(bg="#1a1a1a")

        self.button_style = {
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

        # Load models
        self.face_detector = cv2.FaceDetectorYN_create(
            "src/models/face_detection_yunet_2023mar.onnx", "", (0, 0))
        self.face_detector.setScoreThreshold(0.6)
        self.face_recognizer = cv2.FaceRecognizerSF_create(
            "src/models/face_recognizer_fast.onnx", "")

        # Shared state
        self.recognition_running = False
        self.recognition_thread = None
        self.stop_flag = False
        self.reference_embeddings = {}  # name -> [embedding, start, end, undef]

        # Temp vars for user registration
        self.temp_face_embedding = None
        self.temp_name_entry = None
        self.temp_start_entry = None
        self.temp_end_entry = None
        self.temp_undef_var = None
        self.face_detection_status_label = None

        self.last_displayed_status_text = ""

        # GUI Elements
        self.status_label = tk.Label(self.root, text="System Initializing...",
                                     font=("Arial", 20, "bold"), fg="#f0f0f0", bg="#1a1a1a")
        self.status_label.pack(pady=(10, 20))

        self.center_frame = tk.Frame(self.root, bg="#1a1a1a")
        self.center_frame.pack(expand=True, fill="both", padx=20, pady=10)


        # Load embeddings
        self.load_embeddings()
        self.back_to_main()

    def load_embeddings(self):
        if os.path.exists(self.EMBEDDINGS_FILE):
            self.reference_embeddings = np.load(self.EMBEDDINGS_FILE, allow_pickle=True).item()
        else:
            self.reference_embeddings = {}

    def save_embeddings(self):
        np.save(self.EMBEDDINGS_FILE, self.reference_embeddings)

    def update_status(self, text, color):
        if text != self.last_displayed_status_text:
            self.status_label.config(text=text, fg=color)
            self.last_displayed_status_text = text
    
    def recognize_loop(self):
        cap = cv2.VideoCapture(1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.face_detector.setInputSize((320, 240))

        frame_counter = 0
        self.last_displayed_status_text = ""

        while not self.stop_flag:
            ret, frame = cap.read()
            if not ret:
                self.root.after(0, self.update_status, "Camera Error", "gray")
                break

            frame = cv2.resize(frame, (320, 240))
            frame_counter += 1

            if frame_counter % 10 == 0:
                _, faces = self.face_detector.detect(frame)
                current_status_text = "Locked"
                current_status_color = "#e74c3c"  # Red for locked

                if faces is not None:
                    for face in faces:
                        aligned = self.face_recognizer.alignCrop(frame, face)
                        feature = self.face_recognizer.feature(aligned)

                        for name, data in self.reference_embeddings.items():
                            ref_emb, start, end, undef = data
                            score = self.face_recognizer.match(
                                feature, ref_emb, cv2.FaceRecognizerSF_FR_COSINE)

                            if score >= self.COSINE_THRESHOLD:
                                current_status_text = f"Unlocked: {name}"
                                current_status_color = "#2ecc71"  # Green for unlocked
                                break
                        if current_status_text.startswith("Unlocked"):
                            break

                self.root.after(0, self.update_status, current_status_text, current_status_color)

            time.sleep(0.01)

        cap.release()

    def start_recognition(self):
        if not self.recognition_running:
            self.stop_flag = False
            #self.recognition_thread = threading.Thread(target=self.recognize_loop, daemon=True)
            #VIDEO LABEL CALL
            self.recognition_thread = threading.Thread(target=self.recognize_loop_video_label, daemon=True)
            self.recognition_thread.start()
            self.recognition_running = True
            
            self.update_video_feed()
        self.last_displayed_status_text = ""
        self.update_status("System Initializing...", "#f0f0f0")

    def stop_recognition(self):
        self.stop_flag = True
        self.recognition_running = False

    def reset_recognition(self):
        self.stop_recognition()
        time.sleep(0.5)
        self.start_recognition()

    def clear_frame(self):
        for widget in self.center_frame.winfo_children():
            widget.destroy()

    def back_to_main(self):
        self.temp_face_embedding = None
        self.temp_name_entry = None
        self.temp_start_entry = None
        self.temp_end_entry = None
        self.temp_undef_var = None
        self.face_detection_status_label = None

        self.clear_frame()

        self.status_label.pack_forget()
        self.status_label.pack(pady=(10, 20))

        main_buttons_frame = tk.Frame(self.center_frame, bg="#1a1a1a")
        main_buttons_frame.pack(pady=10)

        tk.Button(main_buttons_frame, text="Add User", command=self.add_user, **self.button_style).pack(fill='x', pady=5)
        tk.Button(main_buttons_frame, text="Delete User", command=self.delete_user, **self.button_style).pack(fill='x', pady=5)
        tk.Button(main_buttons_frame, text="Reset Recognition", command=self.reset_recognition, **self.button_style).pack(fill='x', pady=5)

        self.start_recognition()

    def add_user(self):
        self.stop_recognition()
        self.clear_frame()
        self.update_status("Maintenance", "orange")

        tk.Label(self.center_frame, text="Name:", bg="#1a1a1a", fg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        self.temp_name_entry = tk.Entry(self.center_frame, bg="#2a2a2a", fg="#f0f0f0",
                                        insertbackground="#f0f0f0", bd=1, relief="solid", font=("Arial", 10))
        self.temp_name_entry.pack(ipadx=5, ipady=3)

        tk.Label(self.center_frame, text="Start Date (YYYY-MM-DD):", bg="#1a1a1a", fg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        self.temp_start_entry = tk.Entry(self.center_frame, bg="#2a2a2a", fg="#f0f0f0",
                                         insertbackground="#f0f0f0", bd=1, relief="solid", font=("Arial", 10))
        self.temp_start_entry.pack(ipadx=5, ipady=3)

        tk.Label(self.center_frame, text="End Date (YYYY-MM-DD):", bg="#1a1a1a", fg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        self.temp_end_entry = tk.Entry(self.center_frame, bg="#2a2a2a", fg="#f0f0f0",
                                       insertbackground="#f0f0f0", bd=1, relief="solid", font=("Arial", 10))
        self.temp_end_entry.pack(ipadx=5, ipady=3)

        self.temp_undef_var = tk.BooleanVar()
        undef_check = tk.Checkbutton(self.center_frame, text="Undefined Period", variable=self.temp_undef_var,
                                     bg="#1a1a1a", fg="#f0f0f0", selectcolor="#2a2a2a",
                                     activebackground="#2a2a2a", activeforeground="#f0f0f0",
                                     font=("Arial", 10, "bold"), relief="flat", bd=0)
        undef_check.pack(pady=10)

        tk.Button(self.center_frame, text="Choose Image", command=self.process_chosen_image, **self.button_style).pack(pady=5)

        self.face_detection_status_label = tk.Label(self.center_frame, text="No image selected.",
                                                    bg="#1a1a1a", fg="#f0f0f0", font=("Arial", 10, "italic"))
        self.face_detection_status_label.pack(pady=(0, 10))

        register_button_frame = tk.Frame(self.center_frame, bg="#1a1a1a")
        register_button_frame.pack(pady=10)

        self.register_user_btn = tk.Button(register_button_frame, text="Add User", command=self.register_user_data,
                                           **self.button_style)
        self.register_user_btn.pack(side=tk.LEFT, padx=5)
        self.register_user_btn.config(state=tk.DISABLED)

        tk.Button(register_button_frame, text="Cancel", command=self.back_to_main, **self.button_style).pack(side=tk.LEFT, padx=5)

    def process_chosen_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not filepath:
            self.face_detection_status_label.config(text="No image selected.", fg="#f0f0f0")
            self.temp_face_embedding = None
            self.register_user_btn.config(state=tk.DISABLED)
            return

        image = cv2.imread(filepath)
        if image is None:
            self.face_detection_status_label.config(text="Error: Could not read image.", fg="#e74c3c")
            self.temp_face_embedding = None
            self.register_user_btn.config(state=tk.DISABLED)
            return

        self.face_detector.setInputSize(image.shape[1::-1])
        _, faces = self.face_detector.detect(image)
        if faces is None or len(faces) == 0:
            self.face_detection_status_label.config(text="No face detected in file.", fg="#e74c3c")
            self.temp_face_embedding = None
            self.register_user_btn.config(state=tk.DISABLED)
            return

        aligned_face = self.face_recognizer.alignCrop(image, faces[0])
        self.temp_face_embedding = self.face_recognizer.feature(aligned_face)
        self.face_detection_status_label.config(text="Face detected in file.", fg="#2ecc71")
        self.register_user_btn.config(state=tk.NORMAL)

    def register_user_data(self):
        if self.temp_face_embedding is None:
            messagebox.showerror("Error", "Please choose an image and detect a face first.")
            return

        name = self.temp_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required.")
            return

        start = self.temp_start_entry.get().strip()
        end = self.temp_end_entry.get().strip()
        undef = self.temp_undef_var.get()

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

        self.reference_embeddings[name] = [self.temp_face_embedding, start, end, undef]
        self.save_embeddings()

        self.temp_face_embedding = None
        self.temp_name_entry = None
        self.temp_start_entry = None
        self.temp_end_entry = None
        self.temp_undef_var = None
        if self.face_detection_status_label:
            self.face_detection_status_label.config(text="No image selected.", fg="#f0f0f0")

        self.back_to_main()

    def delete_user(self):
        self.stop_recognition()
        self.clear_frame()
        self.update_status("Maintenance", "orange")

        tk.Label(self.center_frame, text="Select a user to delete:", bg="#1a1a1a", fg="#f0f0f0",
                 font=("Arial", 10, "bold")).pack(pady=(10, 0))

        listbox = tk.Listbox(self.center_frame, bg="#2a2a2a", fg="#f0f0f0", selectbackground="#007bff",
                             selectforeground="white", font=("Arial", 10), bd=1, relief="solid")
        for name in self.reference_embeddings:
            listbox.insert(tk.END, name)
        listbox.pack(pady=5, padx=10, fill="both", expand=True)

        def confirm_delete():
            selected = listbox.curselection()
            if selected:
                name = listbox.get(selected[0])
                del self.reference_embeddings[name]
                self.save_embeddings()
                self.back_to_main()
            else:
                messagebox.showwarning("No Selection", "Please select a user to delete.")

        button_frame = tk.Frame(self.center_frame, bg="#1a1a1a")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Delete", command=confirm_delete, **self.button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.back_to_main, **self.button_style).pack(side=tk.LEFT, padx=5)


