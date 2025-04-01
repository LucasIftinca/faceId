import cv2
import numpy as np

#Functie incarcare modele preantrenate detectie si recunoastere faciala
def load_models():
    face_detector = cv2.FaceDetectorYN_create(r"C:\Users\stefa\OneDrive\Desktop\Nokia\Face-Recognition---Test\src\models\face_detection_yunet_2023mar.onnx", "", (0,0))
    face_detector.setScoreThreshold(0.85)
    
    face_recognizer = cv2.FaceRecognizerSF_create(r"C:\Users\stefa\OneDrive\Desktop\Nokia\Face-Recognition---Test\src\models\face_recognizer_fast.onnx", "")
    
    return face_detector, face_recognizer

def load_embeddings():
    try:
        data = np.load(r"C:\Users\stefa\OneDrive\Desktop\Nokia\Face-Recognition---Test\data\embeddings.npy", allow_pickle=True)
        embeddings = data.item() if data.size > 0 else {}
    except(ValueError,EOFError):
        embeddings = {}
        
    return embeddings

