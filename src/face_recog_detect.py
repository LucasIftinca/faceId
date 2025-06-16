
import cv2, time, threading
import numpy as np
from PIL import Image, ImageTk 

from src.config import *
from src.embeddings_control import *

# Shared state
# Shared state
recognition_running = False
recognition_thread = None
stop_flag = False
cap = None  




def recognize_loop(root, video_label, status_label):
    global stop_flag, last_displayed_status_text, cap

    reference_embeddings = load_embeddings()
    
    cap = cv2.VideoCapture(1)
    
    #input_width, input_height = 200, 200
    FACE_DETECTOR.setInputSize((INPUT_WIDTH, INPUT_HEIGHT))

    frame_counter = 0
    last_displayed_status_text = "" 

    while not stop_flag:
        ret, frame = cap.read()
        if not ret:
            root.after(0, update_status, "Camera Error", "gray")
            
            # Adăugăm un mesaj de eroare vizual pe label-ul video
            if video_label and not stop_flag: # Nu afișa eroare dacă thread-ul se oprește oricum
                blank_img = np.zeros((INPUT_WIDTH, INPUT_HEIGHT, 3), dtype=np.uint8)
                cv2.putText(blank_img, "Camera Error", (50, INPUT_HEIGHT // 2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                img = Image.fromarray(blank_img)
                imgtk = ImageTk.PhotoImage(image=img)
                video_label.imgtk = imgtk
                video_label.config(image=imgtk)
            time.sleep(1) # Așteaptă înainte de a reîncerca
            continue # Treci la următoarea iterație pentru a reîncerca
            # break # Nu mai dăm break, ci încercăm continuu să deschidem camera

        frame_display = cv2.resize(frame, (INPUT_WIDTH, INPUT_HEIGHT))
        frame_process = frame_display.copy()

        frame_counter += 1

        if frame_counter % 10 == 0:
            _, faces = FACE_DETECTOR.detect(frame_process)
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

                    aligned = FACE_RECOGNIZER.alignCrop(frame_process, largest_face)
                    feature = FACE_RECOGNIZER.feature(aligned)

                    for name, data in reference_embeddings.items():
                        ref_emb, start, end, undef = data 
                        score = FACE_RECOGNIZER.match(feature, ref_emb, cv2.FaceRecognizerSF_FR_COSINE)

                        if score >= COSINE_THRESHOLD:
                            current_status_text = f"Unlocked: {name}"
                            current_status_color = "#2ecc71"  
                            break 
            
            root.after(0, update_status, status_label, current_status_text, current_status_color)
        
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

    
def start_recognition(root, video_label,status_label):
    global recognition_running, recognition_thread, stop_flag, last_displayed_status_text
    if not recognition_running:
        stop_flag = False
        # Asigură-te că video_label este vizibil
        if video_label is not None and video_label.winfo_exists():
            video_label.pack(pady=10)
        
        if status_label is not None and status_label.winfo_exists():
            status_label.pack(pady=10)


        recognition_thread = threading.Thread(target=recognize_loop, args= (root, video_label, status_label), daemon=True)
        recognition_thread.start()
        recognition_running = True
    last_displayed_status_text = "" 
    
    if status_label is not None:
        update_status(status_label, "System Initializing...", "#000000")
        print("STARTED RECOGNITION SUCCESFULLY")

def stop_recognition(video_label):
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
    print("STOPPED RECOGNITION SUCCESFULLY")

def reset_recognition(root, video_label, status_label):
    print("RESETED RECOGNITION SUCCESFULLY")
    stop_recognition(video_label)
    time.sleep(0.1)
    start_recognition(root, video_label, status_label)
    

    
def update_status(status_label, text, color):
    global last_displayed_status_text
    

    if text != last_displayed_status_text:
        if status_label is not None:
            status_label.config(text=text, fg=color)
            last_displayed_status_text = text
