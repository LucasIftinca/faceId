import bcrypt
import os

from src.config import PASSWORD_FILE

def load_password():
    if not os.path.exists(PASSWORD_FILE):
        create_initial_password_file()  # Create the password file if it doesn't exist
    with open(PASSWORD_FILE, 'rb') as f:  
        return f.read()  

def save_new_password(new_password):
    try:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())  # Hash the new password with a random salt
        with open(PASSWORD_FILE, 'wb') as f:  
            f.write(hashed_password)  # Write the new hashed password to the file
        return True  
    except Exception as e:
        return False  

def verify_password(check_password, correct_password):
    return bcrypt.checkpw(check_password.encode('utf-8'), correct_password)  # Compare the provided password with the stored hash

def create_initial_password_file():
    if not os.path.exists(PASSWORD_FILE):  # Check if the password file exists
        default_password = b'1234'  # Set a default password
        hashed_password = bcrypt.hashpw(default_password, bcrypt.gensalt())  # Hash the default password
        with open(PASSWORD_FILE, 'wb') as f:  
            f.write(hashed_password)  # Write the initial hashed password

create_initial_password_file()  # Call the function to ensure the file exists at startup