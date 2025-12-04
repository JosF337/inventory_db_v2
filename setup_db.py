"""
DATABASE SETUP SCRIPT
---------------------
Description: Reads the CSV file, cleans data, creates missing columns, 
             and initializes the SQLite database.
"""
import pandas as pd
import sqlite3
import os

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'data', 'inventory.csv') # Looks in 'data' folder
DB_FILE = os.path.join(BASE_DIR, 'inventory.db')

def init_db():
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: Could not find {CSV_FILE}")
        print("Please create a 'data' folder and put your 'inventory.csv' inside it.")
        return

    print("Reading CSV file...")
    # Read as string to preserve leading zeros in serial numbers
    df = pd.read_csv(CSV_FILE, dtype=str)

    # 1. CLEAN COLUMN NAMES
    # Remove spaces, newlines, and convert to lowercase
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(' ', '_', regex=False)
    df.columns = df.columns.str.replace('\n', '_', regex=False)
    
    # Drop useless columns (like the old 'slno' or 'unnamed')
    cols_to_drop = [c for c in df.columns if 'unnamed' in c or 'slno' in c]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    # 2. GENERATE NEW ID
    # We ignore the CSV's ID and create a fresh 1, 2, 3... sequence
    df.insert(0, 'id', range(1, 1 + len(df)))

    # 3. ENSURE ALL COLUMNS EXIST
    # If your CSV is old, it might miss these new fields. We add them as empty.
    required_columns = [
        'inventory_name', 'serial_no', 'make', 'model', 'hardware_type', 
        'spec', 'location', 'status', 'purchase_date', 
        'warranty__period', 'vendor', 'bill_details'
    ]

    for col in required_columns:
        if col not in df.columns:
            print(f"   -> Adding missing column: {col}")
            df[col] = None # Fill with empty values

    # 4. SAVE TO DATABASE
    conn = sqlite3.connect(DB_FILE)
    df.to_sql('items', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"✅ Success! Database created at: {DB_FILE}")
    print(f"   Total Items: {len(df)}")
    print(f"   Columns: {list(df.columns)}")

if __name__ == "__main__":
    init_db()