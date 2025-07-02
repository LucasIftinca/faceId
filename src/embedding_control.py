import numpy as np
import os
from src.config import EMBEDDINGS_FILE

# Shared state for embeddings
reference_embeddings = {}

##### LOADING EMBEDDINGS ######
def load_embeddings():
    global reference_embeddings
    if os.path.exists(EMBEDDINGS_FILE):
        try:
            reference_embeddings = np.load(EMBEDDINGS_FILE, allow_pickle=True).item()
        except Exception as e:
            print(f"Error loading embeddings: {e}. Initializing with empty dictionary.")
            reference_embeddings = {}
    else:
        reference_embeddings = {}
    print(f"Loaded {len(reference_embeddings)} embeddings.")

##### SAVING EMBEDDINGS ######
def save_embeddings():
    try:
        np.save(EMBEDDINGS_FILE, reference_embeddings)
        print(f"Saved {len(reference_embeddings)} embeddings.")
    except Exception as e:
        print(f"Error saving embeddings: {e}")

 
def get_all_user_names():
    return list(reference_embeddings.keys())

def get_user_data(name):
    return reference_embeddings.get(name)

def get_all_users_data():
    return reference_embeddings.copy()

def add_embedding(name, embedding, start_date, end_date, undef_period):
    reference_embeddings[name] = [embedding, start_date, end_date, undef_period]
    save_embeddings()


def remove_embedding(name):
    if name in reference_embeddings:
        del reference_embeddings[name]
        save_embeddings()
        return True
    return False

# Initialize embeddings on module load
load_embeddings()