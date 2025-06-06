import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from src.face_recognition_utils.face_recognition import *
from src.face_recognition_utils.face_detection import *
from src.face_recognition_utils.model_loader import *


add_data_dictionary("Levente", "06/06", "06/06", -1, r"/home/r0bb1/Desktop/Nokia/Face_Detection (Copy)/data/images/capac.jpg")

dict = load_dictionary()

print(dict)