# embedding_storage.py
import os
import numpy as np
from src.config import EMBEDDINGS_FILE

global embeddings_dict

def load_embeddings():
    
    if os.path.exists(EMBEDDINGS_FILE):
        embeddings_dict = np.load(EMBEDDINGS_FILE, allow_pickle = True).item()
    else:
        embeddings_dict = {}
    
    return embeddings_dict


def save_embeddings(embeddings_dict):
    np.save(EMBEDDINGS_FILE, embeddings_dict)
