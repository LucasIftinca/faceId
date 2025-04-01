import os
import cv2
from utils.loadings import load_models, load_embeddings
from utils. face_func import refresh_embeddings, process_frame

# Director principal
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Director imagini
IMAGES_DIR = os.path.join(BASE_DIR, "data", "images")

# Initializare modele
face_detector, face_recognizer = load_models()

# Refresh file embedding-uri
refresh_embeddings(IMAGES_DIR, face_detector, face_recognizer)

# Initializare dictitionar embeddinng-uri
embeddings = load_embeddings()

capture = cv2.VideoCapture(0)

if not capture.isOpened:
    print("EROARE CAMERA")
    exit(0)
    
frame_count = 0

# Bucla infinita pentru inregistrare video
while True:
    result, frame = capture.read()
    if result is False:
        cv2.waitKey(0)
        break
    
    frame = cv2.resize(frame, (0, 0), fx=0.4, fy=0.4)
    
    frame_count += 1
    # Setare numar de frame-uri la care se face 1 detection
    if frame_count % 5 == 0:
        # Apelare functie ce proceseaza frame-ul(detectie+match+actiune)
        frame = process_frame(frame, face_detector, face_recognizer, embeddings)
    
    cv2.imshow("Face Recognition", frame)
    
    # Conditie de iesire
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    
# Preventie leakage resurse
capture.release()
cv2.destroyAllWindows()



