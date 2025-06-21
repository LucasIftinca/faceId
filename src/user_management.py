from src.embedding_control import add_embedding, remove_embedding, get_all_user_names, get_user_data
from datetime import datetime

class UserManagement:
    def __init__(self):
        pass
    
######## ADD USER ##########
    def add_user(self, name, embedding, start_date_str, end_date_str, undef_period):
        if not name:
            return False, "Name is required."
        if embedding is None:
            return False, "Face embedding is missing. Please detect a face."

        if not undef_period:
            if not start_date_str or not end_date_str:
                return False, "Start and End dates are required for a defined period."
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                if start_date > end_date:
                    return False, "Start date cannot be after end date."
            except ValueError:
                return False, "Invalid date format. Please use YYYY-MM-DD."

        add_embedding(name, embedding, start_date_str, end_date_str, undef_period)
        return True, f"User '{name}' added successfully."
    
######### DELETE USER ###########
    def delete_user(self, name):
        if remove_embedding(name):
            return True, f"User '{name}' deleted successfully."
        return False, f"User '{name}' not found."

######## DELETE USER DATA TO DISPLAY ########
    def get_registered_users(self):
        users_display = []
        for name in get_all_user_names():
            data = get_user_data(name)
            if data:
                display_text = f"{name}"
                if data[3]: # undef_period True
                    display_text += " (Undefined)"
                else:
                    display_text += f" ({data[1]} to {data[2]})" # Date start + end
                users_display.append((name, display_text)) 
        return users_display
