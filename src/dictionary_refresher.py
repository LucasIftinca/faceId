import numpy as np
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
EMBEDDINGS_FILE = os.path.join(SCRIPT_DIR, "faces.npy")                                                             

def load_embeddings():                                                                                             
    if os.path.exists(EMBEDDINGS_FILE):
        print(f"Loading embeddings from {EMBEDDINGS_FILE}") 
        return np.load(EMBEDDINGS_FILE, allow_pickle=True).item()
    print(f"No embeddings file found at {EMBEDDINGS_FILE}. Starting with empty dictionary.")
    return {}

def save_embeddings(embeddings_dict):                                                                               
    print(f"Saving updated embeddings to {EMBEDDINGS_FILE}") 
    np.save(EMBEDDINGS_FILE, embeddings_dict)

def refresh_access_periods():                                                                                      

    print(f"[{datetime.now()}] Starting daily access refresh...")
    
    current_embeddings = load_embeddings()
    if not current_embeddings:
        print("No embeddings found or file does not exist. Nothing to refresh.")
        return

    users_to_remove = []
    today = datetime.now().date()

    for name, data in current_embeddings.items():                                                                   
       
        _, start_date_str, end_date_str, is_undefined_period = data

        if not is_undefined_period:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                if today > end_date:
                    users_to_remove.append(name)
                    print(f"User '{name}' access expired on {end_date_str}. Marked for removal.")
            except ValueError:
                print(f"Warning: Invalid end date format for user '{name}': {end_date_str}. Skipping.")
        else:
            print(f"User '{name}' has an undefined access period. Skipping date check.")

    if users_to_remove:
        for user_name in users_to_remove:
            del current_embeddings[user_name]
            print(f"Removed user '{user_name}' from the system.")
        save_embeddings(current_embeddings)
        print("Embeddings file updated successfully.")
    else:
        print("No users with expired access found. No changes made.")

    print(f"[{datetime.now()}] Daily access refresh completed.")

if __name__ == "__main__":
    refresh_access_periods()