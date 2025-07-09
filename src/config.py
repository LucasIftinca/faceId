import cv2



# --- File Paths ---
EMBEDDINGS_FILE = "data/faces.npy"
# Make sure these ONNX model files are in a 'models' directory
FACE_DETECTION_MODEL = "models/face_detection_yunet_2023mar.onnx"
FACE_RECOGNIZER_MODEL = "models/face_recognizer_fast.onnx"

# --- Interface Settings ---
DEFAULT_APP_WIDTH = 790
DEFAULT_APP_HEIGHT = 470
# --- Recognition  ---
COSINE_THRESHOLD = 0.4
DEFAULT_PROCESS_FRAME_RATE = 4

# --- TIMERS ---
VERIFY_TIMER = 7000

# --- Camera/Video Settings ---
DEFAULT_VIDEO_WIDTH = 260
DEFAULT_VIDEO_HEIGHT = 210
DEFAULT_PROCESS_WIDTH = 320
CAMERA_URL = 0
#CAMERA_URL = r"rtsp://admin:adminadmin1@192.168.1.108:554/cam/realmonitor?channel=1&subtype=1"
#CAMERA_URL = "http://192.168.1.133:4747/video"

# --- Admin Settings ---
ADMIN_PASSWORD = "1234"

# --- Colors ---
COLOR_PRIMARY_BG = "#1a1a1a"      
COLOR_TEXT_LIGHT = "#f0f0f0"       
COLOR_SUCCESS_GREEN = "#2ecc71"    
COLOR_ERROR_RED = "#e74c3c"        
COLOR_WARNING_ORANGE = "orange"         
COLOR_IDLE_GRAY = "gray"   
COLOR_INFO_BLUE = "#429ee9"         

DATE_DISPLAY_LABEL_STYLE = {
    "bg": "#9497f1",  # Background color for date display labels
    "fg": COLOR_TEXT_LIGHT,
    "font": ("Helvetica", 10),
    "relief": "solid",
    "borderwidth": 1,
    "width": 12, # A fixed width can help with alignment
    "anchor": "w" # Align text to the west (left)
}

# General button style
BASE_BUTTON_STYLE = {
    "fg": "#f0f0f0",
    "font": ("Arial", 12, "bold"),
    "relief": "flat",
    "borderwidth": 0,
    "highlightthickness": 0,
    "activebackground": "#0056b3",
    "activeforeground": "#f0f0f0",
    "padx": 10,
    "pady": 5,
}

###################### Specific button styles inheriting from BASE_BUTTON_STYLE

VERIFY_BUTTON_STYLE = {
    **BASE_BUTTON_STYLE,
    "bg": "#2ecc71",
    "font": ("Arial", 16, "bold"),
    "padx": 15,
    "pady": 8,
    "width": 15,
    "height": 2,
    "activebackground": "#218838", 
}

ADMIN_SETTINGS_BUTTON_STYLE = {
    **BASE_BUTTON_STYLE,
    "bg": "#007bff",
    "font": ("Arial", 16, "bold"),
    "padx": 10,
    "pady": 5,
    "width": 15,
}

LOGIN_BUTTON_STYLE = {
    **BASE_BUTTON_STYLE,
    "bg": "#2ecc71",
    "font": ("Arial", 14, "bold"),
    "padx": 13,
    "pady": 7,
    "width": 7,
}

CANCEL_BUTTON_STYLE = {
    **BASE_BUTTON_STYLE,
    "bg": "#e74c3c", 
    "font": ("Arial", 14, "bold"),
    "padx": 13,
    "pady": 7,
    "width": 7,
}

ADMIN_OPTION_BUTTON_STYLE = {
    **BASE_BUTTON_STYLE,
    "bg": "#007bff",
    "font": ("Arial", 14, "bold"),
    "padx": 13,
    "pady": 7,
}

DELETE_BUTTON_STYLE = {
    **BASE_BUTTON_STYLE,
    "bg": "#007bff", 
    "font": ("Arial", 14, "bold"),
    "padx": 13,
    "pady": 7,
    "width": 10,
}

CHOOSE_IMAGE_BUTTON_STYLE = {
    **BASE_BUTTON_STYLE,
    "bg": "#007bff",
    "font": ("Arial", 12, "bold"),
    "padx": 13,
    "pady": 5,
    "width": 15,
}

REGISTER_USER_BUTTON_STYLE = {
    **BASE_BUTTON_STYLE,
    "bg": "#007bff",
    "font": ("Arial", 14, "bold"),
    "padx": 13,
    "pady": 7,
}

INPUT_FIELD_STYLE = {
    "bg": "#2a2a2a",
    "fg": "#f0f0f0",
    "insertbackground": "#f0f0f0", # Cursor color
    "bd": 1,
    "relief": "solid",
    "font": ("Arial", 14)
}

LABEL_STYLE = {
    "bg": "#1a1a1a",
    "fg": "#f0f0f0",
    "font": ("Arial", 15, "bold")
}

STATUS_LABEL_STYLE = {
    "font": ("Arial", 20, "bold"),
    "bg": "#1a1a1a",
}

ERROR_LABEL_STYLE = {
    "bg": "#1a1a1a",
    "fg": "#e74c3c",
    "font": ("Arial", 12, "bold")
}

INFO_LABEL_STYLE = {
    "bg": "#1a1a1a",
    "fg": "#f0f0f0",
    "font": ("Arial", 13, "italic")
}

CHECKBOX_STYLE = {
    "bg": "#1a1a1a",
    "fg": "#f0f0f0",
    "selectcolor": "#2a2a2a",
    "activebackground": "#2a2a2a",
    "activeforeground": "#f0f0f0",
    "font": ("Arial", 13, "bold"),
    "relief": "flat",
    "bd": 0
}

LISTBOX_STYLE = {
    "bg": "#2a2a2a",
    "fg": "#f0f0f0",
    "selectbackground": "#007bff",
    "selectforeground": "white",
    "font": ("Arial", 12),
    "bd": 1,
    "relief": "solid",
}