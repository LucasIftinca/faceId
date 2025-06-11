import cv2
import numpy as np
import os 


from src.config import EMBEDDINGS_FILE, DETECTION_MODEL_PATH, RECOGNITION_MODEL_PATH


# #Functie incarcare modele preantrenate detectie si recunoastere faciala
# def load_models():
#     face_detector = cv2.FaceDetectorYN_create(r"src/models/face_detection_yunet_2023mar.onnx", "", (0,0))
#     face_detector.setScoreThreshold(0.85)
    
#     face_recognizer = cv2.FaceRecognizerSF_create(r"src/models/face_recognizer_fast.onnx", "")
    
#     return face_detector, face_recognizer

def load_dictionary():
    try:
        data = np.load(r"data/embeddings_test.npy", allow_pickle=True)
        embeddings = data.item() if data.size > 0 else {}
    except(ValueError,EOFError):
        embeddings = {}
    
    return embeddings

def load_embeddings():
    global reference_embeddings
    if os.path.exists(EMBEDDINGS_FILE):
        reference_embeddings = np.load(EMBEDDINGS_FILE, allow_pickle=True).item()
    else:
        reference_embeddings = {}
        
def save_embeddings():
    np.save(EMBEDDINGS_FILE, reference_embeddings)