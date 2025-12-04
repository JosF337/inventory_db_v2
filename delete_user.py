"""
ADMIN TOOL: DELETE USER
-----------------------
Usage: Run this script to permanently remove a user from the database.
"""
import sqlite3
import os

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = 'inventory.db'
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

def delete_user():
    print("--- 🗑️  DELETE USER ---")
    
    # 1. Get Input
    username = input("Enter Username to delete: ").strip()
    
    if not username:
        print("❌ Username cannot be empty.")
        return

    # 2. Confirm Action (Safety First!)
    confirm = input(f"⚠️  Are you sure you want to delete '{username}'? (yes/no): ").lower()
    
    if confirm != 'yes':
        print("❌ Operation cancelled.")
        return

    # 3. Execute Delete
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists first
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User '{username}' not found.")
        else:
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            print(f"\n✅ SUCCESS! User '{username}' has been deleted.")
            
        conn.close()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    delete_user()