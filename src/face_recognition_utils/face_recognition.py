import cv2
import os
import numpy as np

from  src.face_recognition_utils.model_loader import *

# Functie procesare frame(detectie+match+actiune)
def process_frame(frame, face_detector, face_recognizer, embeddings):
    # Apel functie detectie fata, retuneaza embedding + date fata(coordonate x,y; width; height ...
    feature, face = recognize_face(frame, face_detector, face_recognizer)
    # Conditie fata detectata
    if face is not None:
        # Apel functie match care returneaza boolean(True/False) + tupla(nume,scor)
        result, user = match(face_recognizer, feature, embeddings)
        # Descompunere tupla user in 2 variabile 
        name, score = user if result else ("UNKNOWN", 0.0)
        
        #ACTIUNE
        
        # Marcare fata cu dreptunghi si text
        box = list(map(int, face[:4]))
        color =(0, 255, 0) if result else (0, 0, 255)
        cv2.rectangle(frame, box, color, 2)
        text = "{0} ({1:.2f})".format(name, score)
        position = (box[0], box[1] - 10)
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Return frame procesat        
    return frame

# Functie detectie fata in frame/img( filename=None pentru executia pe frame unde se specifica doar 3 argumente)
def recognize_face(frame, face_detector, face_recognizer, filename=None):
    # Extragere 2 din 3 valori returnare de .shape ( _ inlocuieste channels ex:RGB,RGBA...)
    height, width, _ = frame.shape
    # Setare input conform cu imaginea
    face_detector.setInputSize((width, height))
    # Extragere valori fete din functia .detect ( _ inlocuieste boolean-ul de verificare)
    _, faces = face_detector.detect(frame)
    
    # Verificare daca functia a fost apelata pe o imagine fara fete   
    if filename is not None and faces is None:
        print(f"Fisierul {filename} nu are fete")
    # Verificare daca functia a fost apelata pe un frame fara fete
    if faces is None:
        return None, None
    
    # Alegerea celei mai mari/aproiate fete pentru economisire de resurse.
    closest_face = max(faces, key = lambda face: face[2] * face[3])
    # Alinierea artificiala a fetei (Cap intors)
    aligned_face = face_recognizer.alignCrop(frame, closest_face)
    # Extragere embedding
    feature = face_recognizer.feature(aligned_face)
    
    # Return embedding si date fata(pentru marcare cu dreptunghi folosind coord fetei)
    return feature, closest_face

# Functie match embedding cu dictionar embeddinguri (one2many)
def match(face_recognizer, feature, embeddings):
    max_score = 0.0
    name = ""
    
    # Iterare print dictionar embeddinguri
    for user, user_feature in zip(embeddings.keys(), embeddings.values()):
        # Obtinere matching score
        # cv2.FACE_RECOGNIZER_SF_FR_COSINE utilizeaza similaritatea cosinusului dintre 2 vectori(embeddinguri)
        score = face_recognizer.match(feature, user_feature[0], cv2.FACE_RECOGNIZER_SF_FR_COSINE)
        # Update maxim gasit
        if score >= max_score:
            max_score = score
            name = user
    # Comparare cu threshold  si returnare boolean(True/False) + tupla (nume, scor)
    if max_score < 0.5:
        return False, ("", 0.0)
    return True, (name, max_score)

# Functie refresh file embeddinguri (images update => file.npy update)
def refresh_embeddings(images_directory,face_detector, face_recognizer):
    #Datele sunt stocate in dictionar
    dictionary = {}
    # Parcurgere director imagini
    for file in os.listdir(images_directory):
        # Obtinere path imagine
        file_path = os.path.join(images_directory,file)
        # Citire imagine
        image = cv2.imread(file_path)
        # Apel functie detectie cu specificare de file(in caz de eroare este afisata imaginea corupta)
        feature, face = recognize_face(image, face_detector, face_recognizer, file)
        # Salt spre urmatoarea iteratie daca nu este identificata o fata
        if face is None:
            continue
        # Trimming la path pentru obtinerea numelui ( /images/popescu.jpg -> popescu)
        user = os.path.splitext(os.path.basename(file))[0]
        # Adaugare in dictionar date obtinute
        dictionary[user] = feature
    # Salvare sub forma de fisier .npy (.npy permite serializarea obiectelor)
    np.save(r"data/embeddings.npy", dictionary)


def delete_data_dictionary(name, old_dict):
    del old_dict["name"]
    
    np.save(r"data/embeddings.npy", old_dict) #CHANGE PATH TO GLOBAL VARIABLE 


def generate_embedding(path):
    face_detector, face_recognizer = load_models()
    
    image = cv2.imread(path)
    
    height, width, _ = image.shape
    # Setare input conform cu imaginea
    face_detector.setInputSize((width, height))
    # Extragere valori fete din functia .detect ( _ inlocuieste boolean-ul de verificare)
    _, faces = face_detector.detect(image)
    
    # Verificare daca functia a fost apelata pe o imagine fara fete   
    if faces is None:
        return None, None
    
    # Alegerea celei mai mari/aproiate fete pentru economisire de resurse.
    closest_face = max(faces, key = lambda face: face[2] * face[3])
    # Alinierea artificiala a fetei (Cap intors)
    aligned_face = face_recognizer.alignCrop(image, closest_face)
    # Extragere embedding
    feature = face_recognizer.feature(aligned_face)
    
    # Return embedding si date fata(pentru marcare cu dreptunghi folosind coord fetei)
    return feature

    
def add_data_dictionary(name, start_date, end_date, unlimited_period, path):
    
    #VARIABELS#
    embedding = generate_embedding(path)
    
    info_emp = [embedding, start_date, end_date, unlimited_period]
    
    data_dict = load_dictionary()
    
    data_dict[name] = info_emp
    
    np.save(r"data/embeddings_test.npy", data_dict) #CHANGE PATH TO GLOBAL VARIABLE 
    

