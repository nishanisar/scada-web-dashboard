import sqlite3

# Connect to database (it will create scada.db if it doesn't exist)
conn = sqlite3.connect('scada.db')
cursor = conn.cursor()

# 1. Create Users Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# 2. Create SCADA Data Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scada_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_name TEXT NOT NULL,
        value REAL NOT NULL,
        status TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# 3. Insert 3 Default Users (Ignore if already exists)
users = [
    ('admin', 'admin123'),
    ('engineer', 'eng123'),
    ('operator', 'op123')
]
try:
    cursor.executemany('INSERT INTO users (username, password) VALUES (?, ?)', users)
except sqlite3.IntegrityError:
    pass # Users already exist

# 4. Insert dummy SCADA data
sample_data = [
    ('Temperature Sensor 1', 45.5, 'Normal'),
    ('Pressure Valve A', 120.0, 'Warning'),
    ('Motor Speed', 1500.0, 'Normal')
]
cursor.executemany('INSERT INTO scada_data (sensor_name, value, status) VALUES (?, ?, ?)', sample_data)

conn.commit()
conn.close()

print("Database 'scada.db' created successfully with tables, 3 users, and sample data!")