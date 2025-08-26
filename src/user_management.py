from src.embedding_control import add_embedding, remove_embedding, get_all_users_data
from datetime import datetime

class UserManagement:
    def __init__(self):
        pass

######## ADD USER ##########
    def add_user(self, name, embedding, start_date_str, end_date_str, undef_period):
        if not name:
            return False, "Name is required."  
        if embedding is None:
            return False, "Face data is missing.."  

        if not undef_period:
            if not start_date_str or not end_date_str:
                return False, "Start and End dates are required."  # Dates are mandatory if not undefined
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")  # Convert start date string to datetime object
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")  
                if start_date > end_date:
                    return False, "Start date cannot be after end date." 
            except ValueError:
                return False, "Invalid date format. Please use YYYY-MM-DD."  # Handle invalid date format

        add_embedding(name, embedding, start_date_str, end_date_str, undef_period)  # Call function to save user data
        return True, f"User '{name}' added successfully."  

######### DELETE USER ###########
    def delete_user(self, name):
        if remove_embedding(name):
            return True, f"User '{name}' deleted successfully."  # Delete user and return success
        return False, f"User '{name}' not found."  # Return failure if user not found

######## DELETE USER DATA TO DISPLAY ########
    def get_registered_users(self):
        users_display = []  # Initialize an empty list for display data
        for name, data in get_all_users_data().items():  # Iterate through all registered users
            display_text = f"{name}"  # Start with the user's name
            if data[3]:
                display_text += "(Undefined)"  # Add "Undefined" for perpetual access
            else:
                display_text += f" ({data[1]} to {data[2]})"  # Add date range for temporary access
            users_display.append((name, display_text))  # Append the tuple of name and display string
        return users_display  