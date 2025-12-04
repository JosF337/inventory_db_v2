"""
DATABASE SETUP SCRIPT (Updated for Users)
-----------------------------------------
"""
import pandas as pd
import sqlite3
import os
from werkzeug.security import generate_password_hash # Hashing library

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'data', 'inventory.csv')
DB_FILE = os.path.join(BASE_DIR, 'inventory.db')

def init_db():
    print("--- 1. INITIALIZING DATABASE ---")
    
    # --- PART A: INVENTORY ITEMS ---
    if os.path.exists(CSV_FILE):
        print("   -> Importing Inventory Data...")
        df = pd.read_csv(CSV_FILE, dtype=str)
        # Clean columns
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('\n', '_')
        cols_to_drop = [c for c in df.columns if 'unnamed' in c or 'slno' in c]
        df = df.drop(columns=cols_to_drop, errors='ignore')
        
        # Add ID if missing
        if 'id' not in df.columns:
            df.insert(0, 'id', range(1, 1 + len(df)))
            
        # Ensure new columns exist
        for col in ['purchase_date', 'warranty__period', 'vendor', 'bill_details']:
            if col not in df.columns: df[col] = None

        conn = sqlite3.connect(DB_FILE)
        df.to_sql('items', conn, if_exists='replace', index=False)
        conn.close()
    else:
        print("   -> No CSV found. Creating empty 'items' table.")
        conn = sqlite3.connect(DB_FILE)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY, inventory_name TEXT, serial_no TEXT, 
                make TEXT, model TEXT, hardware_type TEXT, spec TEXT, 
                location TEXT, status TEXT, purchase_date TEXT, 
                warranty__period TEXT, vendor TEXT, bill_details TEXT
            )
        ''')
        conn.close()

    # --- PART B: USERS TABLE (New!) ---
    print("   -> Setting up Users Table...")
    conn = sqlite3.connect(DB_FILE)
    
    # Create Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create a Default Admin User (admin / admin123)
    # We check if empty first to avoid duplicates
    existing_user = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    if not existing_user:
        hashed_pw = generate_password_hash("admin123")
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", hashed_pw))
        print("   -> ✅ Default Admin created: User='admin', Pass='admin123'")
    
    conn.commit()
    conn.close()
    print(f"✅ SUCCESS! Database ready at: {DB_FILE}")

if __name__ == "__main__":
    init_db()