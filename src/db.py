import os
import psycopg2
from dotenv import load_dotenv
import hashlib
from datetime import datetime

load_dotenv()

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('PORT', '5432')
}

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS activity_log (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50),
            action VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

def log_activity(username, action):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO activity_log (username, action) VALUES (%s, %s)",
        (username, action)
    )
    conn.commit()
    cur.close()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    hashed_password = hash_password(password)
    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
                (username, hashed_password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None

def add_user(username, password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        hashed_password = hash_password(password)
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                   (username, hashed_password))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        return False

def get_user_stats(username):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT action, COUNT(*) as count 
        FROM activity_log 
        WHERE username = %s 
        GROUP BY action
    """, (username,))
    stats = cur.fetchall()
    cur.close()
    conn.close()
    return stats