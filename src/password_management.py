import bcrypt
import os

from src.config import PASSWORD_FILE

def load_password():
    if not os.path.exists(PASSWORD_FILE):
        create_initial_password_file()
    with open(PASSWORD_FILE, 'rb') as f:
        return f.read()

def save_new_password(new_password):
    try:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        with open(PASSWORD_FILE, 'wb') as f:
            f.write(hashed_password)
        return True
    except Exception as e:
        return False

def verify_password(check_password, correct_password):
    return bcrypt.checkpw(check_password.encode('utf-8'), correct_password)

def create_initial_password_file():
    if not os.path.exists(PASSWORD_FILE):
        default_password = b'1234'
        hashed_password = bcrypt.hashpw(default_password, bcrypt.gensalt())
        with open(PASSWORD_FILE, 'wb') as f:
            f.write(hashed_password)
            
create_initial_password_file()
