import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import time

try:
    import RPi.GPIO as GPIO
    GPIO_PIN_OUTPUT = 17 # Pin 17
    _gpio_enabled_at_startup = True
    print(f"RPi.GPIO imported. GPIO control enabled on pin {GPIO_PIN_OUTPUT}.")
except ImportError:
    print("RPi.GPIO not found. GPIO control disabled.")
    _gpio_enabled_at_startup = False
except Exception as e:
    print(f"Error importing RPi.GPIO: {e}. GPIO control disabled.")
    _gpio_enabled_at_startup = False

from src.config import (
    ADMIN_PASSWORD, COLOR_PRIMARY_BG, COLOR_TEXT_LIGHT, COLOR_ERROR_RED,
    COLOR_WARNING_ORANGE, COLOR_IDLE_GRAY, COLOR_SUCCESS_GREEN,
    DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT, STATUS_LABEL_STYLE,
    VERIFY_BUTTON_STYLE, ADMIN_SETTINGS_BUTTON_STYLE, LOGIN_BUTTON_STYLE,
    CANCEL_BUTTON_STYLE, ADMIN_OPTION_BUTTON_STYLE, DELETE_BUTTON_STYLE,
    CHOOSE_IMAGE_BUTTON_STYLE, REGISTER_USER_BUTTON_STYLE, INPUT_FIELD_STYLE,
    LABEL_STYLE, ERROR_LABEL_STYLE, INFO_LABEL_STYLE, CHECKBOX_STYLE, LISTBOX_STYLE, CAMERA_URL, VERIFY_TIMER, DEFAULT_PROCESS_WIDTH
)
from src.embedding_control import reference_embeddings
from src.face_recognition import detect_and_recognize_face, get_embedding_from_image
from src.user_management import UserManagement

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Access Control System")
        self.root.geometry("720x420")
        self.root.configure(bg=COLOR_PRIMARY_BG)

        self.status_label = tk.Label(self.root, **STATUS_LABEL_STYLE)
        self.status_label.pack(pady=(10, 10))
        self.update_status("System Initializing...", COLOR_IDLE_GRAY)

        self.main_content_frame = tk.Frame(self.root, bg=COLOR_PRIMARY_BG)
        self.main_content_frame.pack(expand=True, fill="both", padx=10, pady=5)

        self.recognition_running = False
        self.recognition_thread = None
        self.stop_flag = False
        self.cap = None
        self.verification_timer = None

        self.verify_button = None

        self.temp_face_embedding = None
        self.temp_name_entry = None
        self.temp_start_entry = None
        self.temp_end_entry = None
        self.temp_undef_var = None
        self.face_detection_status_label = None
        self.register_user_btn = None

        self.admin_password_entry = None
        self.login_error_label = None

        self.user_manager = UserManagement()

        self.gpio_enabled = _gpio_enabled_at_startup
        if self.gpio_enabled:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(GPIO_PIN_OUTPUT, GPIO.OUT)
                GPIO.output(GPIO_PIN_OUTPUT, GPIO.LOW)
                print(f"GPIO pin {GPIO_PIN_OUTPUT} set up as output and set to LOW.")
            except Exception as e:
                print(f"Failed to set up GPIO: {e}. GPIO control disabled.")
                self.gpio_enabled = False

        self.video_label = None
        self.back_to_main()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_status(self, text, color):
        if self.status_label:
            if text != self.status_label.cget("text") or color != self.status_label.cget("fg"):
                self.status_label.config(text=text, fg=color)

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def update_video_label_placeholder(self, text="Waiting . . ."):
        if self.video_label is None or not self.video_label.winfo_exists():
            return

        blank_img = np.zeros((DEFAULT_VIDEO_HEIGHT, DEFAULT_VIDEO_WIDTH, 3), dtype=np.uint8)
        bgr_color = self.hex_to_rgb(COLOR_PRIMARY_BG)[::-1]
        blank_img[:,:] = bgr_color

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.9
        font_thickness = 2
        text_color = (200, 200, 200)

        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x = (DEFAULT_VIDEO_WIDTH - text_size[0]) // 2
        text_y = (DEFAULT_VIDEO_HEIGHT + text_size[1]) // 2

        cv2.putText(blank_img, text, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        img = Image.fromarray(blank_img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.config(image=imgtk)
        self.video_label.image = imgtk

    def _cleanup_recognition_state(self, status_text="Idle", status_color=COLOR_IDLE_GRAY):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

        if self.gpio_enabled:
            try:
                GPIO.output(GPIO_PIN_OUTPUT, GPIO.LOW)
            except Exception as e:
                print(f"Error setting GPIO LOW during cleanup: {e}")

        self.recognition_running = False
        self.stop_flag = False
        self.root.after(0, self.update_video_label_placeholder)
        self.root.after(0, self.update_status, status_text, status_color)

        if self.verify_button and self.verify_button.winfo_exists():
            self.root.after(0, lambda: self.verify_button.config(state=tk.NORMAL))

        if self.verification_timer:
            self.root.after_cancel(self.verification_timer)
            self.verification_timer = None

    def recognize_loop(self):
        gpio_high_active = False

        try:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(CAMERA_URL)
                if not self.cap.isOpened():
                    raise RuntimeError("Failed to open camera.")

            frame_counter = 0
            current_status_text = "Locked"
            current_status_color = COLOR_ERROR_RED

            while not self.stop_flag:
                ret, frame = self.cap.read()
                if not ret:
                    raise RuntimeError("No camera feed or stream ended unexpectedly.")

                frame_display = cv2.resize(frame, (DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT))
                
                PROCESS_HEIGHT = int(frame.shape[0] * (DEFAULT_PROCESS_WIDTH / frame.shape[1]))
                frame_process = cv2.resize(frame, (DEFAULT_PROCESS_WIDTH, PROCESS_HEIGHT))
                process_input_size = (DEFAULT_PROCESS_WIDTH, PROCESS_HEIGHT)

                bbox = None
                frame_counter += 1

                if frame_counter % 10 == 0:
                    recognized_name, detected_bbox_scaled = detect_and_recognize_face(
                        frame_process, reference_embeddings, process_input_size
                    )
                    
                    if detected_bbox_scaled:
                        scale_factor_x = DEFAULT_VIDEO_WIDTH / DEFAULT_PROCESS_WIDTH
                        scale_factor_y = DEFAULT_VIDEO_HEIGHT / PROCESS_HEIGHT
                        x, y, w, h = detected_bbox_scaled
                        bbox = (int(x * scale_factor_x), int(y * scale_factor_y),
                                int(w * scale_factor_x), int(h * scale_factor_y))

                    if recognized_name:
                        current_status_text = f"Unlocked: {recognized_name}"
                        current_status_color = COLOR_SUCCESS_GREEN
                        if self.gpio_enabled and not gpio_high_active:
                            try:
                                GPIO.output(GPIO_PIN_OUTPUT, GPIO.HIGH)
                                gpio_high_active = True
                            except Exception as e:
                                print(f"Error setting GPIO HIGH: {e}")
                    else:
                        current_status_text = "Locked"
                        current_status_color = COLOR_ERROR_RED
                        if self.gpio_enabled and gpio_high_active:
                            try:
                                GPIO.output(GPIO_PIN_OUTPUT, GPIO.LOW)
                                gpio_high_active = False
                            except Exception as e:
                                print(f"Error setting GPIO LOW: {e}")

                    self.root.after(0, self.update_status, current_status_text, current_status_color)

                if bbox:
                    x, y, w, h = bbox
                    if recognized_name:
                        cv2.rectangle(frame_display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    else:
                        cv2.rectangle(frame_display, (x, y), (x + w, y + h), (0, 0, 255), 2)
                
                img = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)

                self.root.after(0, lambda: self.video_label.config(image=imgtk))
                self.root.after(0, lambda: setattr(self.video_label, '_imgtk', imgtk))

                time.sleep(0.01)

        except RuntimeError as e:
            self.root.after(0, self._cleanup_recognition_state, str(e), COLOR_ERROR_RED)
        except Exception as e:
            self.root.after(0, self._cleanup_recognition_state, f"Error: {e}", COLOR_ERROR_RED)
        finally:
            self.root.after(0, self._cleanup_recognition_state)

    def start_recognition(self):
        if self.recognition_running:
            return
        if self.verification_timer:
            self.root.after_cancel(self.verification_timer)
            self.verification_timer = None

        if self.verify_button:
            self.verify_button.config(state=tk.DISABLED)

        self.stop_flag = False
        self.recognition_thread = threading.Thread(target=self.recognize_loop, daemon=True)
        self.recognition_thread.start()
        self.recognition_running = True
        self.update_status("Initializing camera...", COLOR_IDLE_GRAY)
        self.verification_timer = self.root.after(VERIFY_TIMER, self.stop_recognition_and_video)

    def stop_recognition_and_video(self):
        if not self.recognition_running and not self.stop_flag:
            return
        self.stop_flag = True
        self.update_status("Stopping recognition...", COLOR_IDLE_GRAY)

    # def reset_recognition_state(self):
    #     self.stop_recognition_and_video()
    #     self.root.after(500, lambda: self.update_status("System Reset", COLOR_IDLE_GRAY))

    def on_closing(self):
        self.stop_recognition_and_video()
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=1.0)
        if self.gpio_enabled:
            try:
                GPIO.cleanup()
            except Exception as e:
                print(f"Error during GPIO cleanup: {e}")
        self.root.destroy()

    def clear_main_content_frame(self):
        for widget in self.main_content_frame.winfo_children():
            if widget != self.video_label:
                widget.destroy()

    def back_to_main(self):
        self.stop_recognition_and_video()
        self.clear_main_content_frame()

        self.temp_face_embedding = None
        self.temp_name_entry = None
        self.temp_start_entry = None
        self.temp_end_entry = None
        self.temp_undef_var = None
        self.face_detection_status_label = None
        self.register_user_btn = None
        if self.login_error_label and self.login_error_label.winfo_exists():
            self.login_error_label.destroy()
            self.login_error_label = None

        if self.video_label is None or not self.video_label.winfo_exists():
            self.video_label = tk.Label(self.main_content_frame, bg=self.main_content_frame["bg"],
                                         width=DEFAULT_VIDEO_WIDTH, height=DEFAULT_VIDEO_HEIGHT)
        self.video_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.update_video_label_placeholder()

        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(1, weight=0)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        button_column_frame = tk.Frame(self.main_content_frame, bg=COLOR_PRIMARY_BG)
        button_column_frame.grid(row=0, column=1, padx=20, pady=0, sticky="ns")

        button_column_frame.grid_rowconfigure(0, weight=1)
        button_column_frame.grid_rowconfigure(1, weight=0)
        button_column_frame.grid_rowconfigure(2, weight=0)
        button_column_frame.grid_rowconfigure(3, weight=1)

        self.verify_button = tk.Button(button_column_frame, text="Verify", command=self.start_recognition,
                                         **VERIFY_BUTTON_STYLE)
        self.verify_button.grid(row=1, column=0, pady=10, sticky="ew")

        tk.Button(button_column_frame, text="Admin Settings", command=self.admin_settings_login,
                    **ADMIN_SETTINGS_BUTTON_STYLE).grid(row=2, column=0, pady=10, sticky="ew")

        self.update_status("Idle", COLOR_IDLE_GRAY)

    def admin_settings_login(self):
        self.stop_recognition_and_video()
        self.clear_main_content_frame()
        self.update_status("Admin Login", COLOR_WARNING_ORANGE)

        if self.video_label and self.video_label.winfo_exists():
            self.video_label.grid_forget()

        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(1, weight=1)
        self.main_content_frame.grid_columnconfigure(2, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(1, weight=1)

        login_frame = tk.Frame(self.main_content_frame, bg=COLOR_PRIMARY_BG)
        login_frame.grid(row=1, column=1, pady=20, sticky="nsew")

        tk.Label(login_frame, text="Password:", **LABEL_STYLE).pack(pady=(0,10))
        self.admin_password_entry = tk.Entry(login_frame, **INPUT_FIELD_STYLE, show='*')
        self.admin_password_entry.pack(ipadx=10, ipady=5)
        self.admin_password_entry.bind("<Return>", lambda event=None: self.check_admin_password())

        self.login_error_label = tk.Label(login_frame, text="", **ERROR_LABEL_STYLE)
        self.login_error_label.pack(pady=(10, 0))

        tk.Button(login_frame, text="Login", command=self.check_admin_password, **LOGIN_BUTTON_STYLE).pack(pady=15)
        tk.Button(login_frame, text="Cancel", command=self.back_to_main, **CANCEL_BUTTON_STYLE).pack(pady=10)

    def check_admin_password(self):
        password = self.admin_password_entry.get().strip()
        if password == ADMIN_PASSWORD:
            if self.login_error_label:
                self.login_error_label.config(text="")
            self.show_admin_options()
        else:
            if self.login_error_label:
                self.login_error_label.config(text="Incorrect password.")
            self.admin_password_entry.delete(0, tk.END)

    def show_admin_options(self):
        self.clear_main_content_frame()
        if self.login_error_label and self.login_error_label.winfo_exists():
            self.login_error_label.destroy()
            self.login_error_label = None

        if self.video_label and self.video_label.winfo_exists():
            self.video_label.grid_forget()
        self.update_status("Admin Mode", COLOR_WARNING_ORANGE)

        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(1, weight=1)
        self.main_content_frame.grid_columnconfigure(2, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(1, weight=1)

        admin_buttons_frame = tk.Frame(self.main_content_frame, bg=COLOR_PRIMARY_BG)
        admin_buttons_frame.grid(row=1, column=1, pady=20, sticky="nsew")

        tk.Button(admin_buttons_frame, text="Add User", command=self.add_user_screen,
                    **ADMIN_OPTION_BUTTON_STYLE).pack(fill='x', pady=8)
        tk.Button(admin_buttons_frame, text="Delete User", command=self.delete_user_screen,
                    **ADMIN_OPTION_BUTTON_STYLE).pack(fill='x', pady=8)
        # tk.Button(admin_buttons_frame, text="Reset System (Idle)",
        #             command=lambda: [self.reset_recognition_state(), self.show_admin_options()],
        #             **ADMIN_OPTION_BUTTON_STYLE).pack(fill='x', pady=8)
        tk.Button(admin_buttons_frame, text="Exit Admin", command=self.back_to_main,
                    **ADMIN_OPTION_BUTTON_STYLE).pack(fill='x', pady=20)

    def add_user_screen(self):
        self.stop_recognition_and_video()
        self.clear_main_content_frame()
        if self.video_label and self.video_label.winfo_exists():
            self.video_label.grid_forget()
        self.update_status("Add User", COLOR_WARNING_ORANGE)

        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(1, weight=1)
        self.main_content_frame.grid_columnconfigure(2, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        add_user_form_frame = tk.Frame(self.main_content_frame, bg=COLOR_PRIMARY_BG)
        add_user_form_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        add_user_form_frame.grid_columnconfigure(0, weight=0)
        add_user_form_frame.grid_columnconfigure(1, weight=1)

        row_idx = 0

        tk.Label(add_user_form_frame, text="Name:", **LABEL_STYLE).grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.temp_name_entry = tk.Entry(add_user_form_frame, **INPUT_FIELD_STYLE)
        self.temp_name_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        row_idx += 1

        tk.Label(add_user_form_frame, text="Start Date (YYYY-MM-DD):", **LABEL_STYLE).grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.temp_start_entry = tk.Entry(add_user_form_frame, **INPUT_FIELD_STYLE)
        self.temp_start_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        row_idx += 1

        tk.Label(add_user_form_frame, text="End Date (YYYY-MM-DD):", **LABEL_STYLE).grid(row=row_idx, column=0, sticky="w", padx=5, pady=3)
        self.temp_end_entry = tk.Entry(add_user_form_frame, **INPUT_FIELD_STYLE)
        self.temp_end_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=3)
        row_idx += 1

        self.temp_undef_var = tk.BooleanVar()
        undef_check = tk.Checkbutton(add_user_form_frame, text="Undefined Period", variable=self.temp_undef_var,
                                         **CHECKBOX_STYLE)
        undef_check.grid(row=row_idx, column=0, columnspan=2, pady=10)
        row_idx += 1

        tk.Button(add_user_form_frame, text="Choose Image", command=self.process_chosen_image,
                    **CHOOSE_IMAGE_BUTTON_STYLE).grid(row=row_idx, column=0, columnspan=2, pady=5)
        row_idx += 1

        self.face_detection_status_label = tk.Label(add_user_form_frame, text="No image selected.", **INFO_LABEL_STYLE)
        self.face_detection_status_label.grid(row=row_idx, column=0, columnspan=2, pady=(0, 10))
        row_idx += 1

        register_button_frame = tk.Frame(add_user_form_frame, bg=COLOR_PRIMARY_BG)
        register_button_frame.grid(row=row_idx, column=0, columnspan=2, pady=5)

        self.register_user_btn = tk.Button(register_button_frame, text="Add User", command=self.register_user_data,
                                                 **REGISTER_USER_BUTTON_STYLE)
        self.register_user_btn.pack(side=tk.LEFT, padx=5)
        self.register_user_btn.config(state=tk.DISABLED)

        tk.Button(register_button_frame, text="Cancel", command=self.show_admin_options,
                    **CANCEL_BUTTON_STYLE).pack(side=tk.LEFT, padx=5)

    def process_chosen_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if not filepath:
            self.temp_face_embedding = None
            self.face_detection_status_label.config(text="No image selected.", fg=COLOR_TEXT_LIGHT)
            self.register_user_btn.config(state=tk.DISABLED)
            return

        embedding, status_msg, status_color = get_embedding_from_image(
            filepath, (DEFAULT_VIDEO_WIDTH, DEFAULT_VIDEO_HEIGHT)
        )
        self.temp_face_embedding = embedding
        self.face_detection_status_label.config(text=status_msg, fg=status_color)

        if embedding is not None:
            self.register_user_btn.config(state=tk.NORMAL)
        else:
            self.register_user_btn.config(state=tk.DISABLED)

    def register_user_data(self):
        name = self.temp_name_entry.get().strip()
        start = self.temp_start_entry.get().strip()
        end = self.temp_end_entry.get().strip()
        undef = self.temp_undef_var.get()

        success, message = self.user_manager.add_user(
            name, self.temp_face_embedding, start, end, undef
        )

        if success:
            messagebox.showinfo("Success", message)
            self.temp_face_embedding = None
            self.temp_name_entry.delete(0, tk.END)
            self.temp_start_entry.delete(0, tk.END)
            self.temp_end_entry.delete(0, tk.END)
            self.temp_undef_var.set(False)
            if self.face_detection_status_label:
                self.face_detection_status_label.config(text="No image selected.", fg=COLOR_TEXT_LIGHT)
            self.register_user_btn.config(state=tk.DISABLED)
            self.show_admin_options()
        else:
            messagebox.showerror("Error", message)

    def delete_user_screen(self):
        self.stop_recognition_and_video()
        self.clear_main_content_frame()
        if self.video_label and self.video_label.winfo_exists():
            self.video_label.grid_forget()
        self.update_status("Delete User", COLOR_WARNING_ORANGE)

        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(1, weight=1)
        self.main_content_frame.grid_columnconfigure(2, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        delete_user_frame = tk.Frame(self.main_content_frame, bg=COLOR_PRIMARY_BG)
        delete_user_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        tk.Label(delete_user_frame, text="Select a user to delete:", **LABEL_STYLE).pack(pady=(10,10))

        listbox_container = tk.Frame(delete_user_frame, bg=COLOR_PRIMARY_BG)
        listbox_container.pack(pady=10, padx=10, fill="both", expand=True)

        scrollbar = tk.Scrollbar(listbox_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.delete_listbox = tk.Listbox(listbox_container, **LISTBOX_STYLE, yscrollcommand=scrollbar.set, height=8)
        self.delete_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.delete_listbox.yview)

        self._populate_delete_listbox()

        button_frame = tk.Frame(delete_user_frame, bg=COLOR_PRIMARY_BG)
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="Delete", command=self.confirm_delete_user,
                    **DELETE_BUTTON_STYLE).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=self.show_admin_options,
                    **CANCEL_BUTTON_STYLE).pack(side=tk.LEFT, padx=10)

    def _populate_delete_listbox(self):
        self.delete_listbox.delete(0, tk.END)
        users = self.user_manager.get_registered_users()
        for actual_name, display_text in users:
            self.delete_listbox.insert(tk.END, display_text)

    def confirm_delete_user(self):
        selected_index = self.delete_listbox.curselection()
        if selected_index:
            selected_name_display = self.delete_listbox.get(selected_index[0])
            actual_name = selected_name_display.split('(')[0].strip()

            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{actual_name}'?"):
                success, message = self.user_manager.delete_user(actual_name)
                if success:
                    self.show_admin_options()
                else:
                    messagebox.showerror("Error", message)
            else:
                messagebox.showinfo("Cancelled", "User deletion cancelled.")
        else:
            messagebox.showwarning("No Selection", "Please select a user to delete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()