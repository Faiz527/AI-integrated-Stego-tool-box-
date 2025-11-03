import os
import psycopg2
from dotenv import load_dotenv
import streamlit as st
import hashlib
from psycopg2 import sql

# Database configuration
load_dotenv()
DB_CONFIG = {
    'dbname': st.secrets["postgres"]["dbname"],
    'user': st.secrets["postgres"]["user"],
    'password': st.secrets["postgres"]["password"],
    'host': st.secrets["postgres"]["host"],
    'port': st.secrets["postgres"]["port"]
}

def get_database_connection():
    try:
        return psycopg2.connect(
            dbname=st.secrets["postgres"]["dbname"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            host=st.secrets["postgres"]["host"],
            port=st.secrets["postgres"]["port"],
            sslmode='require',
            options="-c timezone=utc"
        )
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

def init_db():
    try:
        conn = get_database_connection()
        if conn is None:
            return False
            
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(50) PRIMARY KEY,
                password VARCHAR(256) NOT NULL
            )
        """)
        
        # Create activity log table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) REFERENCES users(username),
                action VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return False

def verify_user(username, password):
    try:
        conn = get_database_connection()
        if conn is None:
            return False
            
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
        conn = get_database_connection()
        if conn is None:
            return False
            
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
        conn = get_database_connection()
        if conn is None:
            return False
            
        cur = conn.cursor()
        cur.execute("INSERT INTO activity_log (username, action) VALUES (%s, %s)",
                   (username, action))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Failed to log activity: {e}")
        return False

def get_user_stats(username):
    try:
        conn = get_database_connection()
        if conn is None:
            return []
            
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