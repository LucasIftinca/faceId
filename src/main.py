# src/main.py
import cv2
from PIL import Image, ImageTk
import os

from utils.loadings import load_models, load_embeddings
from utils.face_func import refresh_embeddings, process_frame

def main(video_label):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    IMAGES_DIR = os.path.join(BASE_DIR, "data", "images")

    face_detector, face_recognizer = load_models()
    refresh_embeddings(IMAGES_DIR, face_detector, face_recognizer)
    embeddings = load_embeddings()

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

        frame = cv2.resize(frame, (300, 220))
        frame_count += 1

        if frame_count % 5 == 0:
            frame = process_frame(frame, face_detector, face_recognizer, embeddings)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(img)

        video_label.configure(image=imgtk)
        video_label.image = imgtk

        video_label.after(10, update_frame)

    update_frame()
