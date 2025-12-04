"""
INVENTORY MANAGEMENT SYSTEM - CONTROLLER
----------------------------------------
Description: Main application logic handling routes, database connections,
             and business logic for the inventory system.
"""

from flask import Flask, render_template, request, redirect, url_for, send_file, Response
import sqlite3
import os
import io
import pandas as pd
import segno
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURATION ---
DB_NAME = 'inventory.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES ---

@app.route('/')
def dashboard():
    """
    Renders the dashboard with Advanced Search functionality.
    """
    query = request.args.get('q')
    conn = get_db_connection()
    
    if query:
        search_term = f"%{query}%"
        # Search across ALL relevant columns
        items = conn.execute('''
            SELECT * FROM items 
            WHERE 
                inventory_name LIKE ? OR 
                serial_no LIKE ? OR 
                make LIKE ? OR 
                model LIKE ? OR 
                location LIKE ? OR 
                vendor LIKE ? OR
                status LIKE ?
        ''', (search_term, search_term, search_term, search_term, search_term, search_term, search_term)).fetchall()
    else:
        items = conn.execute('SELECT * FROM items').fetchall()
    
    # Fetch unique names for the "Suggestions" dropdown
    all_names = conn.execute('SELECT DISTINCT inventory_name FROM items').fetchall()
    
    conn.close()
    return render_template('index.html', items=items, active_page='home', suggestions=all_names)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    """
    Handles creating a new item.
    """
    if request.method == 'POST':
        conn = get_db_connection()
        # Auto-increment ID logic
        max_id = conn.execute('SELECT MAX(id) FROM items').fetchone()[0]
        new_id = (max_id or 0) + 1 
        
        conn.execute('''
            INSERT INTO items (id, inventory_name, serial_no, make, model, hardware_type, 
                             spec, purchase_date, warranty__period, vendor, bill_details, location, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            new_id,
            request.form['inventory_name'], request.form['serial_no'],
            request.form['make'], request.form['model'], request.form['hardware_type'],
            request.form['spec'], request.form['purchase_date'], request.form['warranty__period'],
            request.form['vendor'], request.form['bill_details'], request.form['location'], request.form['status']
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    
    return render_template('form.html', item=None, active_page='add')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    """
    Handles updating an existing item.
    """
    conn = get_db_connection()
    
    if request.method == 'POST':
        conn.execute('''
            UPDATE items SET 
                inventory_name = ?, serial_no = ?, make = ?, model = ?, hardware_type = ?, 
                spec = ?, purchase_date = ?, warranty__period = ?, vendor = ?, bill_details = ?, 
                location = ?, status = ?
            WHERE id = ?
        ''', (
            request.form['inventory_name'], request.form['serial_no'],
            request.form['make'], request.form['model'], request.form['hardware_type'],
            request.form['spec'], request.form['purchase_date'], request.form['warranty__period'],
            request.form['vendor'], request.form['bill_details'], request.form['location'], request.form['status'],
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('view_item', id=id))
    
    item = conn.execute('SELECT * FROM items WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if item is None:
        return "Item not found", 404
        
    return render_template('form.html', item=item, active_page='detail')

@app.route('/item/<int:id>')
def view_item(id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if item is None:
        return "Item not found", 404
        
    return render_template('detail.html', item=item, active_page='detail')

# --- MOVED UP: The Delete Route must be defined BEFORE app.run() ---
@app.route('/delete/<int:id>', methods=['POST'])
def delete_item(id):
    """
    Handles deleting an item.
    """
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/qr/<int:id>')
def download_qr(id):
    conn = get_db_connection()
    item = conn.execute('SELECT inventory_name FROM items WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if item:
        link = url_for('view_item', id=id, _external=True)
        qr = segno.make_qr(link)
        buffer = io.BytesIO()
        qr.save(buffer, kind='png', scale=10, border=1)
        buffer.seek(0)
        
        # Clean filename
        safe_name = "".join([c for c in item['inventory_name'] if c.isalnum() or c in (' ','-')]).strip()
        filename = f"{safe_name}.png"
        
        return send_file(buffer, mimetype='image/png', as_attachment=True, download_name=filename)
    
    return "Item not found", 404

@app.route('/export')
def export_data():
    """
    Exports the entire database to CSV.
    """
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM items", conn)
        conn.close()
        
        csv_data = df.to_csv(index=False)
        
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=inventory_export.csv"}
        )
    except Exception as e:
        return f"Export failed: {e}"

# --- APP START (Must be at the very end) ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)