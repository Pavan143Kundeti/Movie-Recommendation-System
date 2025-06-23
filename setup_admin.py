import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import database

def ensure_admin_exists():
    """
    Checks if an admin user exists and creates one if it doesn't.
    This ensures that there is always a default admin account.
    """
    print("Checking for admin user...")
    # Check if a user with the username 'admin' already exists.
    existing_admin = database.get_user_by_username('admin')
    
    if existing_admin:
        print("Admin user already exists. Resetting password...")
        # Reset the password for the existing admin user.
        success = database.update_user_password(existing_admin['email'], 'admin123')
        if success:
            print("Admin password has been reset to 'admin123'.")
        else:
            print("Failed to reset admin password.")
    else:
        print("Admin user not found. Creating a new admin account...")
        username = 'admin'
        email = 'admin@example.com' # Default email for admin
        password = 'admin123'
        
        # Add the new admin user to the database.
        success = database.add_user(username, email, password, role='admin')
        
        if success:
            print(f"Admin user '{username}' created successfully with password '{password}'.")
        else:
            print(f"Failed to create admin user.")

if __name__ == "__main__":
    try:
        # We need to create the tables first to ensure the users table exists.
        database.create_tables()
        database.create_otp_table()
        ensure_admin_exists()
    except Exception as e:
        print(f"An error occurred during admin setup: {e}") 