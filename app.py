"""
INVENTORY MANAGEMENT SYSTEM - CONTROLLER (SECURED)
--------------------------------------------------
Description: Main application logic handling routes, database connections,
             authentication, and business logic.
"""

# ==============================================================================
# 1. IMPORTS & CONFIGURATION
# ==============================================================================
from flask import Flask, render_template, request, redirect, url_for, send_file, Response, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
import sqlite3
import os
import io
import pandas as pd
import segno
from datetime import datetime

app = Flask(__name__)

# SECURITY CONFIGURATION
# ----------------------
# Needed for user sessions. In production, use a secure random key.
app.secret_key = 'dev_key_change_this_in_production' 
DB_NAME = 'inventory.db'

# FLASK-LOGIN SETUP
# -----------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirect here if not logged in


# ==============================================================================
# 2. DATABASE HELPERS
# ==============================================================================
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DB_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# ==============================================================================
# 3. AUTHENTICATION MODELS & LOGIC
# ==============================================================================
class User(UserMixin):
    """
    User class required by Flask-Login. 
    Matches the 'users' table in the database.
    """
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user_data = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        if not user_data:
            return None
        return User(user_data['id'], user_data['username'], user_data['password_hash'])

@login_manager.user_loader
def load_user(user_id):
    """Reloads the user object from the user ID stored in the session."""
    return User.get(user_id)


# ==============================================================================
# 4. ERROR HANDLERS
# ==============================================================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="We couldn't find the page you were looking for.", code=404), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message="Internal Server Error. Please contact support.", code=500), 500


# ==============================================================================
# 5. AUTHENTICATION ROUTES (Login / Logout)
# ==============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login requests."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"--- DEBUG: Attempting login for '{username}' ---") # DEBUG PRINT
        
        conn = get_db_connection()
        user_data = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user_data:
            print(f"--- DEBUG: User found. ID: {user_data['id']}") # DEBUG PRINT
            # Verify Password
            if check_password_hash(user_data['password_hash'], password):
                print("--- DEBUG: Password correct! Logging in...") # DEBUG PRINT
                user = User(user_data['id'], user_data['username'], user_data['password_hash'])
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                print("--- DEBUG: Password INCORRECT.") # DEBUG PRINT
                flash("Invalid username or password")
        else:
            print("--- DEBUG: User NOT found in database.") # DEBUG PRINT
            flash("Invalid username or password")
            
    return render_template('login.html')

# ==============================================================================
# 6. MAIN DASHBOARD ROUTES
# ==============================================================================
@app.route('/')
@login_required # <--- THIS LOCKS THE DASHBOARD
def dashboard():
    """
    Renders the dashboard with Advanced Search functionality.
    """
    query = request.args.get('q')
    conn = get_db_connection()
    
    if query:
        search_term = f"%{query}%"
        items = conn.execute('''
            SELECT * FROM items 
            WHERE 
                inventory_name LIKE ? OR serial_no LIKE ? OR 
                make LIKE ? OR model LIKE ? OR 
                location LIKE ? OR vendor LIKE ? OR status LIKE ?
        ''', (search_term, search_term, search_term, search_term, search_term, search_term, search_term)).fetchall()
    else:
        items = conn.execute('SELECT * FROM items').fetchall()
    
    # Fetch suggestions for autocomplete
    all_names = conn.execute('SELECT DISTINCT inventory_name FROM items').fetchall()
    conn.close()
    
    return render_template('index.html', items=items, active_page='home', suggestions=all_names, user=current_user)


# ==============================================================================
# 7. CRUD ROUTES (Add, Edit, View, Delete)
# ==============================================================================
@app.route('/add', methods=['GET', 'POST'])
@login_required # <--- LOCKED
def add_item():
    """Handles creating a new item."""
    if request.method == 'POST':
        conn = get_db_connection()
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
@login_required # <--- LOCKED
def edit_item(id):
    """Handles updating an existing item."""
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
        return render_template('error.html', message="Item not found", code=404), 404
        
    return render_template('form.html', item=item, active_page='detail')


@app.route('/item/<int:id>')
@login_required # <--- LOCKED
def view_item(id):
    """Renders the detailed view of a single item."""
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if item is None:
        return render_template('error.html', message="Item not found", code=404), 404
        
    return render_template('detail.html', item=item, active_page='detail')


@app.route('/delete/<int:id>', methods=['POST'])
@login_required # <--- LOCKED
def delete_item(id):
    """Handles deleting an item."""
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


# ==============================================================================
# 8. UTILITY ROUTES (QR Code & Export)
# ==============================================================================
@app.route('/qr/<int:id>')
@login_required # <--- LOCKED
def download_qr(id):
    """Generates and downloads a QR code."""
    conn = get_db_connection()
    item = conn.execute('SELECT inventory_name FROM items WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if item:
        link = url_for('view_item', id=id, _external=True)
        qr = segno.make_qr(link)
        buffer = io.BytesIO()
        qr.save(buffer, kind='png', scale=10, border=1)
        buffer.seek(0)
        
        safe_name = "".join([c for c in item['inventory_name'] if c.isalnum() or c in (' ','-')]).strip()
        return send_file(buffer, mimetype='image/png', as_attachment=True, download_name=f"{safe_name}.png")
    
    return render_template('error.html', message="QR Source Not Found", code=404), 404


@app.route('/export')
@login_required # <--- LOCKED
def export_data():
    """Exports the entire database to CSV."""
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
        return render_template('error.html', message=f"Export Failed: {e}", code=500), 500


# ==============================================================================
# 9. APP START
# ==============================================================================
if __name__ == '__main__':
    # host='0.0.0.0' allows external access (Critical for Docker)
    app.run(debug=True, port=5000, host='0.0.0.0')