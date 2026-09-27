from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'super_secret_scada_key'

# SQL Server Connection Details
DB_DRIVER = '{SQL Server}'
DB_SERVER = r'DESKTOP-7KSLQEG\SQLEXPRESS'
DB_DATABASE = 'scada_db'

def get_db_connection():
    conn_str = f'DRIVER={DB_DRIVER};SERVER={DB_SERVER};DATABASE={DB_DATABASE};Trusted_Connection=yes;'
    conn = pyodbc.connect(conn_str)
    return conn

def fetch_all_as_dict(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_one_as_dict(cursor):
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    return None

# --- AUTHENTICATION ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = fetch_one_as_dict(cursor)
        conn.close()
        
        if user:
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials! Try again.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists!', 'danger')
        else:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('New user created successfully! Please login.', 'success')
            conn.close()
            return redirect(url_for('login'))
            
        conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# --- SCADA DASHBOARD & CRUD ROUTES ---
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scada_data ORDER BY id DESC')
    data = fetch_all_as_dict(cursor)
    conn.close()
    
    total_sensors = len(data)
    warnings = len([d for d in data if str(d['status']).lower() == 'warning'])
    
    return render_template('dashboard.html', data=data, user=session['username'], total=total_sensors, warnings=warnings)

# YAHAN CHANGES KI GAYI HAIN (Location add kiya gaya hai)
@app.route('/add', methods=['POST'])
def add_data():
    if 'username' in session:
        sensor = request.form['sensor_name']
        value = float(request.form['value'])
        status = request.form['status']
        location = request.form['location'] # Naya column data pakra
        
        conn = get_db_connection()
        cursor = conn.cursor()
        # Insert query mein location add kiya
        cursor.execute('''
            INSERT INTO scada_data (sensor_name, value, status, location) 
            VALUES (?, ?, ?, ?)
        ''', (sensor, value, status, location))
        conn.commit()
        conn.close()
        flash('Sensor Data Added with Location!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
def delete_data(id):
    if 'username' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM scada_data WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash('Data Deleted!', 'warning')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)