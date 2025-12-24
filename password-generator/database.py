import sqlite3
import os

DB = 'Base.db'

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE passwords (
                id INTEGER PRIMARY KEY,
                username TEXT,
                service TEXT,
                password TEXT,
                length INTEGER,
                complexity TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES ('admin', 'admin')")
        conn.commit()
        conn.close()

def register_user(username, password):
    try:
        conn = sqlite3.connect(DB)
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def verify_user(username, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username = ? AND password_hash = ?", (username, password))
    res = cur.fetchone()
    conn.close()
    return res is not None

def save_password(username, service, password, length, complexity):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO passwords (username, service, password, length, complexity) VALUES (?, ?, ?, ?, ?)",
                 (username, service, password, length, complexity))
    conn.commit()
    conn.close()

def get_user_passwords(username):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT service, password, length, complexity, created_at FROM passwords WHERE username = ? ORDER BY created_at DESC", (username,))
    rows = cur.fetchall()
    conn.close()
    return [{'service': r[0], 'password': r[1], 'length': r[2], 'complexity': r[3], 'timestamp': r[4]} for r in rows]

def get_all_users():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT username FROM users")
    users = [r[0] for r in cur.fetchall()]
    conn.close()
    return users

def get_all_passwords():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT username, service, password, length, complexity, created_at FROM passwords ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [{'username': r[0], 'service': r[1], 'password': r[2], 'length': r[3], 'complexity': r[4], 'timestamp': r[5]} for r in rows]