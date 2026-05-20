import cv2
import numpy as np
from src.config import FACE_DETECTION_MODEL, FACE_RECOGNIZER_MODEL, COSINE_THRESHOLD

# Threshold for how much the depth data deviates from a perfect flat plane.
# Tilted phones usually score under 10-15. Real faces score much higher due to the nose/eyes.
DEPTH_RESIDUAL_THRESHOLD = 20.0

# Models loaded for once and globally
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
def detect_and_recognize_face(frame, depth_frame, reference_embeddings, input_size):
    if face_detector is None or face_recognizer is None:
        print("Models not loaded, cannot perform recognition.")
        return None, None

    ############### Face detection ################
    face_detector.setInputSize(input_size)
    _, faces = face_detector.detect(frame)

    if faces is None or len(faces) == 0:
        return None, None

    faces_np = np.array(faces)
    valid_faces = faces_np[np.where((faces_np[:, 2] > 0) & (faces_np[:, 3] > 0))]  # Filter out invalid faces

    if len(valid_faces) == 0:
        return None, None

    areas = valid_faces[:, 2] * valid_faces[:, 3]
    largest_face = valid_faces[np.argsort(areas)[::-1][0]]  # Get the largest face by area

    bbox = tuple(map(int, largest_face[:4]))  # x, y, w, h

    ############### Depth Anti-Spoofing Check ######
    if depth_frame is not None:
        x, y, w, h = bbox

        # Ensure coordinates are within frame bounds to avoid slicing errors
        x, y = max(0, x), max(0, y)
        w = min(w, depth_frame.shape[1] - x)
        h = min(h, depth_frame.shape[0] - y)

        face_depth_region = depth_frame[y:y + h, x:x + w].astype(float)

        if face_depth_region.size > 0:
            # 1. Filter out 0 values (Kinect infrared blind spots)
            valid_mask = face_depth_region > 0

            # If the Kinect can't read the depth (e.g. holding a glossy phone screen that reflects IR away)
            if np.sum(valid_mask) < 0.3 * face_depth_region.size:
                print("Spoof detected: Cannot read depth (reflective surface).")
                return "Spoof Detected", bbox

            # 2. Get X, Y coordinates and Z depth values for valid pixels
            yy, xx = np.indices(face_depth_region.shape)
            xx_valid = xx[valid_mask]
            yy_valid = yy[valid_mask]
            zz_valid = face_depth_region[valid_mask]

            # 3. Fit a flat 2D plane to the depth data (Equation: Z = a*X + b*Y + c)
            A = np.c_[xx_valid, yy_valid, np.ones_like(xx_valid)]
            # Calculate the coefficients of the best-fitting plane
            C, _, _, _ = np.linalg.lstsq(A, zz_valid, rcond=None)

            # 4. Calculate how much the actual face deviates from this flat plane
            zz_fit = np.dot(A, C)
            residuals = zz_valid - zz_fit
            residual_variance = np.var(residuals)

            # A flat phone (even tilted) will have a low residual variance.
            # A 3D face will have high residual variance (nose, cheeks, eye sockets don't fit on a flat board).
            if residual_variance < DEPTH_RESIDUAL_THRESHOLD:
                print(f"Spoof detected: Flat surface detected. Residual variance: {residual_variance:.2f}")
                return "Spoof Detected", bbox

    aligned_face = face_recognizer.alignCrop(frame, largest_face)

    ################ Face recognition ###############
    feature = face_recognizer.feature(aligned_face)  # Extract the face embedding

    ################ Face matching ##################
    recognized_name = None
    for name, data in reference_embeddings.items():
        ref_emb = data[0]
        score = face_recognizer.match(feature, ref_emb, cv2.FaceRecognizerSF_FR_COSINE)  # Compare embeddings
        if score >= COSINE_THRESHOLD:
            recognized_name = name
            break

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

    areas = valid_faces[:, 2] * valid_faces[:, 3]
    largest_face = valid_faces[np.argsort(areas)[::-1][0]]

    aligned_face = face_recognizer.alignCrop(img_resized, largest_face)
    embedding = face_recognizer.feature(aligned_face)  # Extract the face embedding

    return embedding, "Face loaded.", "green"