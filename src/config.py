import cv2


#ALL THE CONSTANTS ARE DECLARED HERE


BUTTON_STYLE = {
    "bg": "#007bff",
    "fg": "white",
    "font": ("Roboto", 20),
    "relief": "flat",
    "borderwidth": 0,
    "highlightthickness": 0,
    "activebackground": "#0056b3",
    "activeforeground": "white",
    "padx": 10,
    "pady": 5,
    "width": 16,
    # "height" :28,
}

ENTRY_STYLE = {
    "bg": "#ffffff",  # Light background for good contrast
    "fg": "#000000",  # Standard black text
    "font": ("Roboto", 20),
    "relief": "flat",
    "highlightthickness": 1,
    "highlightbackground": "#007bff",  # Blue border like the button
    "highlightcolor": "#0056b3",      # Highlighted border on focus
    "insertbackground": "#000000",    # Cursor color
    "width": 16,                      # Adjust width to match button width visually
}

LABEL_STYLE_STATUS ={
    "bg": "#2b2b2b",  # Light background for good contrast
    "fg": "#FFFFFF",  # Standard black text
    "font": ("Roboto", 20),
    "relief": "flat",
}

LABEL_STYLE_MISC ={
    "bg": "#2b2b2b",  # Light background for good contrast
    "fg": "#FFFFFF",  # Standard black text
    "font": ("Roboto", 10),
    "relief": "flat",
}

#SERIALIZED DICTONARY RELATIVE PATH
EMBEDDINGS_FILE = "data/faces.npy" 
#RECOGNTION MODEL RELATIVE PATH
RECOGNITION_MODEL = "models/face_recognizer_fast.onnx"
#DETECTION MODEL RELATIVE PATH
DETECTION_MODEL = "models/face_detection_yunet_2023mar.onnx"
#CAMERA URL 
CAMERA_URL = "rtsp://admin:adminadmin1@192.168.1.108:554/cam/realmonitor?channel=1&subtype=1"
#
COSINE_THRESHOLD = 0.5

FACE_DETECTOR = cv2.FaceDetectorYN_create(DETECTION_MODEL,"", (0, 0) )
FACE_DETECTOR.setScoreThreshold(0.6)
FACE_RECOGNIZER = cv2.FaceRecognizerSF_create(RECOGNITION_MODEL, " ")

INPUT_WIDTH, INPUT_HEIGHT = 320, 220