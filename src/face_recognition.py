import cv2
import numpy as np
from src.config import FACE_DETECTION_MODEL, FACE_RECOGNIZER_MODEL, COSINE_THRESHOLD

# Models loaded for once and globaly
try:
    face_detector = cv2.FaceDetectorYN_create(FACE_DETECTION_MODEL, "", (0, 0))
    face_detector.setScoreThreshold(0.6)
    face_recognizer = cv2.FaceRecognizerSF_create(FACE_RECOGNIZER_MODEL, "")
    print("Face detection and recognition models loaded successfully.")
except Exception as e:
    print(f"Error loading face recognition models: {e}")
    face_detector = None
    face_recognizer = None

####### RECOGNIZING LOOP ########
def detect_and_recognize_face(frame, reference_embeddings, input_size):
    
    if face_detector is None or face_recognizer is None:
        print("Models not loaded, cannot perform recognition.")        
        return None, None
    
############### Face detection ################
    face_detector.setInputSize(input_size)
    _, faces = face_detector.detect(frame)

    if faces is None or len(faces) == 0:
        return None, None 

    faces_np = np.array(faces)
    # Filter out invalid faces (width or height <= 0)
    valid_faces = faces_np[np.where((faces_np[:, 2] > 0) & (faces_np[:, 3] > 0))]

    # In case there are no faces
    if len(valid_faces) == 0:
        return None, None 

    # Extract largest face
    areas = valid_faces[:, 2] * valid_faces[:, 3]
    largest_face = valid_faces[np.argsort(areas)[::-1][0]]

    # Coordonates for match box
    bbox = tuple(map(int, largest_face[:4])) # x, y, w, h

    # Align and get feature for recognition
    aligned_face = face_recognizer.alignCrop(frame, largest_face)
    
################ Face recognition ###############
    feature = face_recognizer.feature(aligned_face)

################ Face matching ##################
    recognized_name = None
    for name, data in reference_embeddings.items():
        ref_emb = data[0] # Embedding at index 0
        score = face_recognizer.match(feature, ref_emb, cv2.FaceRecognizerSF_FR_COSINE)
        if score >= COSINE_THRESHOLD:
            recognized_name = name
            break # Stopping after finding a match

    return recognized_name, bbox


####### EXTRACTING FROM FILE #########
def get_embedding_from_image(filepath, input_size):

    if face_detector is None or face_recognizer is None:
        return None, "Error", "red"

    image = cv2.imread(filepath)
    if image is None:
        return None, "Error: Could not read image file.", "red"

    img_resized = cv2.resize(image, input_size)
    face_detector.setInputSize(input_size)

    _, faces = face_detector.detect(img_resized)

    if faces is None or len(faces) == 0:
        return None, "No valid face detected.", "red"

    faces_np = np.array(faces)
    valid_faces = faces_np[np.where((faces_np[:, 2] > 0) & (faces_np[:, 3] > 0))]

    if len(valid_faces) == 0:
        return None, "No valid face detected.", "red"

    # Getting the largest face
    areas = valid_faces[:, 2] * valid_faces[:, 3]
    largest_face = valid_faces[np.argsort(areas)[::-1][0]]

    aligned_face = face_recognizer.alignCrop(img_resized, largest_face)
    embedding = face_recognizer.feature(aligned_face)

    return embedding, "Face loaded.", "green"