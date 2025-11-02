import os
import psycopg2
from dotenv import load_dotenv
import streamlit as st
import hashlib

# Database configuration
load_dotenv()
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'steganography'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Password'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('PORT', '5432')
}

def init_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")

def verify_user(username, password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
                    (username, hashed_password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user is not None
    except Exception as e:
        st.error(f"Login verification failed: {e}")
        return False

def add_user(username, password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                   (username, hashed_password))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Registration failed: {e}")
        return False

def log_activity(username, action):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("INSERT INTO activity_log (username, action) VALUES (%s, %s)",
                   (username, action))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Failed to log activity: {e}")

def get_user_stats(username):
    try:
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
    except Exception as e:
        st.error(f"Failed to get user stats: {e}")
        return []

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()