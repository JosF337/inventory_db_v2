"""
ADMIN TOOL: CREATE USER
-----------------------
Usage: Run this script to add a new user to the database.
"""
import sqlite3
import os
from werkzeug.security import generate_password_hash
import getpass # Hides password when typing

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = 'inventory.db'
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

def create_user():
    print("--- 👤 ADD NEW USER ---")
    
    # 1. Get Inputs
    username = input("Enter Username: ").strip()
    if not username:
        print("❌ Username cannot be empty.")
        return

    # getpass hides the typing for security
    password = getpass.getpass("Enter Password: ")
    confirm_pass = getpass.getpass("Confirm Password: ")

    if password != confirm_pass:
        print("❌ Passwords do not match!")
        return
    
    if len(password) < 4:
        print("❌ Password is too short (min 4 chars).")
        return

    # 2. Hash the Password (Never store plain text!)
    hashed_pw = generate_password_hash(password)

    # 3. Save to Database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        
        print(f"\n✅ SUCCESS! User '{username}' has been created.")
        print("   You can now log in with this account.")
        
    except sqlite3.IntegrityError:
        print(f"\n❌ ERROR: User '{username}' already exists.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    create_user()