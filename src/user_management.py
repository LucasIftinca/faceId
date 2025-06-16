import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime


from src.embeddings_control import *
from src.config import *


from tkinter import messagebox
from datetime import datetime

    
def register_emp_data(entry_name, entry_date_start, entry_date_stop, temp_undef_var, face_embedding):
    embeddings_dict = load_embeddings()

    if face_embedding is None:
        messagebox.showerror("Error", "Please choose an image and detect a face first.")
        return

    name = entry_name.get().strip()
    if not name:
        messagebox.showerror("Error", "Name is required.")
        return

    if name in embeddings_dict:
        if not messagebox.askyesno("Warning", f"User '{name}' already exists. Do you want to overwrite their data?"):
            return

    start_date = entry_date_start.get().strip()
    end_date = entry_date_stop.get().strip()
    undef = temp_undef_var.get()  # ✅ retrieve boolean value

    if not undef:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                messagebox.showerror("Error", "Start date cannot be after end date.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return
    else:
        start = None
        end = None

    
    embeddings_dict[name] = [face_embedding, start, end, undef]
    save_embeddings(embeddings_dict)
    messagebox.showinfo("Success", f"User '{name}' added successfully.")
    
def process_chosen_image(label_valid_image, button_add_emp_data, data_holder):
    global temp_face_embedding

    filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not filepath:
        label_valid_image.config(text="No image selected.", fg="#f0f0f0")
        return
    image = cv2.imread(filepath)
    if image is None:
        label_valid_image.config(text="Error: Could not read image.", fg="#e74c3c")
        temp_face_embedding = None
        button_add_emp_data.config(state=tk.DISABLED)
        return

    img_height, img_width = image.shape[:2]
    FACE_DETECTOR.setInputSize((img_width, img_height)) 
    
    _, faces = FACE_DETECTOR.detect(image)
    if faces is None or len(faces) == 0:
        label_valid_image.config(text="No face detected in file.", fg="#e74c3c")
        temp_face_embedding = None
        button_add_emp_data.config(state=tk.DISABLED)
        return

    faces_np = np.array(faces)
    valid_faces = faces_np[np.where((faces_np[:, 2] > 0) & (faces_np[:, 3] > 0))]
    
    if len(valid_faces) > 0:
        areas = valid_faces[:, 2] * valid_faces[:, 3]
        largest_face = valid_faces[np.argsort(areas)[::-1][0]]
        
        aligned_face = FACE_RECOGNIZER.alignCrop(image, largest_face)
        temp_face_embedding = FACE_RECOGNIZER.feature(aligned_face)
        label_valid_image.config(text="Face detected in file.", fg="#2ecc71")
        button_add_emp_data.config(state=tk.NORMAL)
    else:
        label_valid_image.config(text="No valid face detected in file.", fg="#e74c3c")
        temp_face_embedding = None
        button_add_emp_data.config(state=tk.DISABLED)
    
    # if temp_face_embedding is not None:
    #     entry_date_start.insert(0, str(temp_face_embedding))
    # else:
    #     entry_date_start.insert(0, "No embedding")
        
    data_holder["embedding"] = temp_face_embedding

def delete_emp(tree, button_delete_emp):
    selected_item = tree.focus()
    if not selected_item:
        button_delete_emp.config(state=tk.DISABLED)
        return

    values = tree.item(selected_item, 'values')
    if not values:
        button_delete_emp.config(state=tk.DISABLED)
        return

    selected_name = values[0]

    embeddings_dict = load_embeddings()
    if selected_name in embeddings_dict:
        if not messagebox.askyesno("Confirm Delete", f"Delete user '{selected_name}'?"):
            return

        del embeddings_dict[selected_name]
        save_embeddings(embeddings_dict)
        tree.delete(selected_item)
        button_delete_emp.config(state=tk.DISABLED)


   
    