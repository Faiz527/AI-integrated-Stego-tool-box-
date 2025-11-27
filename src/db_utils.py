"""
Database Utilities Module
==========================
Handles all database operations including user management,
operation logging, and statistics retrieval.
"""

import os
import sys
import psycopg2
from psycopg2 import sql, Error
from pathlib import Path
import hashlib

# ============================================================================
#                    ENVIRONMENT SETUP (CRITICAL!)
# ============================================================================

# Get project root (parent of src folder)
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

print(f"📁 Project root: {PROJECT_ROOT}")
print(f"📄 Looking for .env at: {ENV_FILE}")
print(f"📌 .env exists: {ENV_FILE.exists()}")

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=str(ENV_FILE), override=True, verbose=False)

# Verify variables loaded
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'stegno_app')
db_user = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', '')

# DEBUG: Print raw values
print(f"\n✅ Loaded environment variables:")
print(f"   DB_HOST = '{db_host}'")
print(f"   DB_PORT = '{db_port}'")
print(f"   DB_NAME = '{db_name}'")
print(f"   DB_USER = '{db_user}'")
print(f"   DB_PASSWORD = '{db_password}'")
print(f"   DB_PASSWORD length = {len(db_password)}")
print(f"   DB_PASSWORD bytes = {db_password.encode()}")

# ============================================================================
#                        DATABASE CONNECTION
# ============================================================================

def get_db_connection():
    """
    Create and return a PostgreSQL database connection.
    """
    try:
        # Get credentials from environment (with defaults)
        host = os.getenv('DB_HOST', 'localhost')
        port = int(os.getenv('DB_PORT', '5432'))
        database = os.getenv('DB_NAME', 'stegno_app')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        
        print(f"\n🔌 Connecting to PostgreSQL...")
        print(f"   Host: {host}:{port}")
        print(f"   Database: {database}")
        print(f"   User: {user}")
        print(f"   Password: '{password}' (length: {len(password)})")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        print(f"✅ Connection successful!")
        return conn
        
    except Error as e:
        print(f"❌ Database connection error: {e}")
        raise Exception(f"Database connection failed: {e}")


def initialize_database():
    """
    Initialize database tables if they don't exist.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("\n📋 Creating database tables...")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ users table")
        
        # Create operations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                operation_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                operation_type VARCHAR(20) NOT NULL,
                method VARCHAR(20) NOT NULL,
                data_size INTEGER,
                is_encrypted BOOLEAN DEFAULT FALSE,
                status VARCHAR(50) DEFAULT 'Success',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ operations table")
        
        # Create activity_log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                activity_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ activity_log table")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database initialized successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False


# ============================================================================
#                        USER MANAGEMENT
# ============================================================================

def hash_password(password):
    """
    Hash password using SHA-256.
    
    Args:
        password (str): Plain text password
    
    Returns:
        str: Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def add_user(username, password):
    """
    Add a new user to the database.
    
    Args:
        username (str): Username
        password (str): Plain text password
    
    Returns:
        bool: True if successful, False if user already exists
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    
    except psycopg2.IntegrityError:
        # Username already exists
        return False
    except Exception as e:
        print(f"❌ Error adding user: {e}")
        return False


def verify_user(username, password):
    """
    Verify user credentials.
    
    Args:
        username (str): Username
        password (str): Plain text password
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s AND password_hash = %s",
            (username, password_hash)
        )
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result is not None
    
    except Exception as e:
        print(f"❌ Error verifying user: {e}")
        return False


def get_user_id(username):
    """
    Get user ID from username.
    
    Args:
        username (str): Username
    
    Returns:
        int: User ID, or None if not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result[0] if result else None
    
    except Exception as e:
        print(f"❌ Error getting user ID: {e}")
        return None


# ============================================================================
#                        OPERATION LOGGING
# ============================================================================

def log_operation(username, operation_type, method, data_size=0, is_encrypted=False, status="✅ Success"):
    """
    Log a steganography operation to the database.
    
    Args:
        username (str): Username performing the operation
        operation_type (str): 'encode' or 'decode'
        method (str): 'LSB', 'DCT', or 'DWT'
        data_size (int): Size of data in bytes
        is_encrypted (bool): Whether message was encrypted
        status (str): Operation status
    
    Returns:
        bool: True if logged successfully, False otherwise
    """
    try:
        user_id = get_user_id(username)
        if not user_id:
            print(f"⚠️  User '{username}' not found, skipping operation log")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO operations 
            (user_id, operation_type, method, data_size, is_encrypted, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (user_id, operation_type, method, data_size, is_encrypted, status))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Logged operation: {operation_type} ({method})")
        return True
    
    except Exception as e:
        print(f"⚠️  Error logging operation: {e}")
        return False


def log_activity(username, action):
    """
    Log user activity to the database.
    
    Args:
        username (str): Username
        action (str): Action description
    
    Returns:
        bool: True if logged successfully
    """
    try:
        user_id = get_user_id(username)
        if not user_id:
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO activity_log (user_id, action, created_at) VALUES (%s, %s, NOW())",
            (user_id, action)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"❌ Error logging activity: {e}")
        return False


# ============================================================================
#                        STATISTICS RETRIEVAL
# ============================================================================

def get_user_stats(username):
    """
    Get operation statistics for a user.
    
    Args:
        username (str): Username
    
    Returns:
        list: List of (method, count) tuples
    """
    try:
        user_id = get_user_id(username)
        if not user_id:
            return []
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT method, COUNT(*) FROM operations 
            WHERE user_id = %s 
            GROUP BY method 
            ORDER BY COUNT(*) DESC
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
    
    except Exception as e:
        print(f"❌ Error getting user stats: {e}")
        return []


def get_operation_stats():
    """
    Fetch global operation statistics from database (all users).
    
    Returns:
        dict: {
            'total_operations': int,
            'total_encodes': int,
            'total_decodes': int,
            'lsb_count': int,
            'dct_count': int,
            'dwt_count': int,
            'encrypted_count': int
        }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total operations
        cursor.execute("SELECT COUNT(*) FROM operations")
        total_ops = cursor.fetchone()[0]
        
        # Get encode/decode split
        cursor.execute(
            "SELECT operation_type, COUNT(*) FROM operations GROUP BY operation_type"
        )
        op_types = dict(cursor.fetchall())
        
        # Get method distribution
        cursor.execute(
            "SELECT method, COUNT(*) FROM operations GROUP BY method"
        )
        methods = dict(cursor.fetchall())
        
        # Get encrypted message count
        cursor.execute("SELECT COUNT(*) FROM operations WHERE is_encrypted = true")
        encrypted = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'total_operations': total_ops,
            'total_encodes': op_types.get('encode', 0),
            'total_decodes': op_types.get('decode', 0),
            'lsb_count': methods.get('LSB', 0),
            'dct_count': methods.get('DCT', 0),
            'dwt_count': methods.get('DWT', 0),
            'encrypted_count': encrypted
        }
    
    except Exception as e:
        print(f"❌ Error fetching operation stats: {e}")
        return None


def get_timeline_data(days=7):
    """
    Fetch operation timeline data for last N days.
    
    Args:
        days (int): Number of days to fetch data for
    
    Returns:
        tuple: (dates_list, operations_list)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM operations
            WHERE created_at >= NOW() - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        
        cursor.execute(query % days)
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if results:
            dates = [row[0] for row in results]
            operations = [row[1] for row in results]
        else:
            dates = []
            operations = []
        
        return dates, operations
    
    except Exception as e:
        print(f"❌ Error fetching timeline data: {e}")
        return [], []


def get_method_distribution():
    """
    Fetch distribution of methods used across all users.
    
    Returns:
        tuple: (methods_list, counts_list)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT method, COUNT(*) FROM operations GROUP BY method ORDER BY COUNT(*) DESC"
        )
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if results:
            methods = [row[0] for row in results]
            counts = [row[1] for row in results]
        else:
            methods = ['LSB', 'DCT', 'DWT']
            counts = [0, 0, 0]
        
        return methods, counts
    
    except Exception as e:
        print(f"❌ Error fetching method distribution: {e}")
        return ['LSB', 'DCT', 'DWT'], [0, 0, 0]


def get_recent_activity(limit=10):
    """
    Fetch recent user operations across all users.
    
    Args:
        limit (int): Number of recent operations to fetch
    
    Returns:
        list: List of operation dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                o.operation_id,
                u.username,
                o.created_at,
                o.operation_type,
                o.method,
                o.data_size,
                o.is_encrypted,
                o.status
            FROM operations o
            JOIN users u ON o.user_id = u.user_id
            ORDER BY o.created_at DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        operations = []
        for row in results:
            operations.append({
                'timestamp': row[2],
                'username': row[1],
                'action': row[3].capitalize(),
                'method': row[4],
                'data_size': f"{row[5] / (1024*1024):.1f} MB" if row[5] else "0 MB",
                'is_encrypted': row[6],
                'status': row[7]
            })
        
        return operations
    
    except Exception as e:
        print(f"❌ Error fetching recent activity: {e}")
        return []