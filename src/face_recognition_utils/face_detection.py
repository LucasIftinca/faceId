# src/main.py
import cv2
from PIL import Image, ImageTk
import os
from customtkinter import CTkImage


# main.py
from src.face_recognition_utils.model_loader import load_models, load_embeddings
from src.face_recognition_utils.face_recognition import refresh_embeddings, process_frame

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMAGES_DIR = os.path.join(BASE_DIR, "data", "images")

face_detector, face_recognizer = load_models()

def face_detection(video_label):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    IMAGES_DIR = os.path.join(BASE_DIR, "data", "images")


    face_detector, face_recognizer = load_models()
    refresh_embeddings(IMAGES_DIR, face_detector, face_recognizer)
    embeddings = load_embeddings()

    # Setare url pentru flux video de la camera IP
    url="rtsp://admin:adminadmin1@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0"

    capture = cv2.VideoCapture(1)
    if not capture.isOpened():
        print("EROARE CAMERA")
        return

    frame_count = 0

    def update_frame():
        nonlocal frame_count
        ret, frame = capture.read()
        if not ret:
            return

        frame_count += 1

        if frame_count % 5 == 0:
            # Run face recognition on the original BGR frame
            frame = process_frame(frame, face_detector, face_recognizer, embeddings)

        # Now resize and convert for display
        frame = cv2.resize(frame, (300, 240))  # or match your label size
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(img)

        video_label.configure(image=imgtk)
        video_label.image = imgtk

        video_label.after(10, update_frame)

    update_frame()
