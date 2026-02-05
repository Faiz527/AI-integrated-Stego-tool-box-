"""
Database Utilities Module
==========================
Handles all PostgreSQL database operations including user management,
operation logging, and activity tracking.
"""

import psycopg2
from psycopg2 import sql
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=str(PROJECT_ROOT / '.env'))

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'stegnography'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Password')
}


def get_db_connection():
    """
    Establish PostgreSQL database connection.
    
    Returns:
        psycopg2.connection: Database connection object
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Database connection successful")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise


def initialize_database():
    """
    Initialize database tables if they don't exist.
    Creates users, operations, and activity_log tables only if missing.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'users'
            )
        """)
        
        if not cursor.fetchone()[0]:
            # Create users table
            cursor.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Created users table")
        
        # Check if operations table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'operations'
            )
        """)
        
        if not cursor.fetchone()[0]:
            # Create operations table
            cursor.execute("""
                CREATE TABLE operations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    method VARCHAR(50),
                    input_image VARCHAR(255),
                    output_image VARCHAR(255),
                    message_size INTEGER,
                    encoding_time FLOAT,
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Created operations table")
        
        # Check if activity_log table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'activity_log'
            )
        """)
        
        if not cursor.fetchone()[0]:
            # Create activity_log table
            cursor.execute("""
                CREATE TABLE activity_log (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    action VARCHAR(255),
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("Created activity_log table")
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database tables initialized successfully")
        print("Database tables initialized successfully (no existing tables were dropped)")
        
    except psycopg2.Error as e:
        logger.error(f"Database initialization failed: {str(e)}")
        print(f"Database initialization failed: {str(e)}")


def add_user(username: str, password_hash: str) -> bool:
    """
    Add a new user to the database.
    
    Args:
        username (str): Username
        password_hash (str): Hashed password
    
    Returns:
        bool: Success status
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"User {username} added successfully")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Failed to add user: {str(e)}")
        return False


def verify_user(username: str, password_hash: str) -> dict:
    """
    Verify user credentials and return user data.
    
    Args:
        username (str): Username
        password_hash (str): Hashed password
    
    Returns:
        dict: Dictionary with user_id if credentials match, None otherwise
              Example: {'user_id': 1, 'username': 'testuser'}
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username FROM users WHERE username = %s AND password_hash = %s",
            (username, password_hash)
        )
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {'user_id': result[0], 'username': result[1]}
        else:
            return None
        
    except psycopg2.Error as e:
        logger.error(f"User verification failed: {str(e)}")
        return None


def log_operation(user_id: int, method: str, input_image: str, output_image: str,
                  message_size: int, encoding_time: float, status: str):
    """
    Log a steganography operation.
    
    Args:
        user_id (int): User ID
        method (str): Steganography method used
        input_image (str): Input image path
        output_image (str): Output image path
        message_size (int): Size of embedded message
        encoding_time (float): Time taken for encoding
        status (str): Operation status
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO operations 
            (user_id, method, input_image, output_image, message_size, encoding_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, method, input_image, output_image, message_size, encoding_time, status))
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Operation logged for user {user_id}")
        
    except psycopg2.Error as e:
        logger.error(f"Failed to log operation: {str(e)}")


def log_activity(user_id: int, action: str, details: str = None):
    """
    Log user activity.
    
    Args:
        user_id (int): User ID
        action (str): Action description
        details (str): Additional details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO activity_log (user_id, action, details) VALUES (%s, %s, %s)",
            (user_id, action, details)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Activity logged for user {user_id}")
        
    except psycopg2.Error as e:
        logger.error(f"Failed to log activity: {str(e)}")


def get_user_operations(user_id: int, limit: int = 10) -> list:
    """
    Get user's recent operations.
    
    Args:
        user_id (int): User ID
        limit (int): Number of records to retrieve
    
    Returns:
        list: List of operations
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, method, input_image, output_image, message_size, encoding_time, status, created_at
            FROM operations
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        operations = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return operations
        
    except psycopg2.Error as e:
        logger.error(f"Failed to retrieve operations: {str(e)}")
        return []


def get_statistics() -> dict:
    """
    Get application statistics.
    
    Returns:
        dict: Statistics data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Total operations
        cursor.execute("SELECT COUNT(*) FROM operations")
        total_operations = cursor.fetchone()[0]
        
        # Operations by method
        cursor.execute("SELECT method, COUNT(*) FROM operations GROUP BY method")
        method_counts = cursor.fetchall()
        
        # Average encoding time
        cursor.execute("SELECT AVG(encoding_time) FROM operations")
        avg_time = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'total_users': total_users,
            'total_operations': total_operations,
            'by_method': dict(method_counts),
            'avg_encoding_time': float(avg_time) if avg_time else 0
        }
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        return {}


def get_operation_stats(days: int = 7) -> dict:
    """
    Get operation statistics for the last N days.
    
    Args:
        days (int): Number of days to retrieve stats for
    
    Returns:
        dict: Statistics data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                method,
                COUNT(*) as count,
                AVG(encoding_time) as avg_time
            FROM operations
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY DATE(created_at), method
            ORDER BY DATE(created_at) DESC
        """, (days,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            'stats': [
                {
                    'date': str(row[0]),
                    'method': row[1],
                    'count': row[2],
                    'avg_time': float(row[3]) if row[3] else 0
                }
                for row in results
            ]
        }
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get operation stats: {str(e)}")
        return {'stats': []}


def get_method_distribution() -> dict:
    """
    Get distribution of operations by method.
    
    Returns:
        dict: Method distribution data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT method, COUNT(*) as count
            FROM operations
            GROUP BY method
        """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {method: count for method, count in results}
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get method distribution: {str(e)}")
        return {}


def get_encode_decode_stats() -> dict:
    """
    Get encoding vs decoding statistics.
    
    Returns:
        dict: Encode/decode statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CASE WHEN output_image IS NOT NULL THEN 'Encode' ELSE 'Decode' END as type,
                COUNT(*) as count
            FROM operations
            GROUP BY type
        """)
        
        results = dict(cursor.fetchall())
        cursor.close()
        conn.close()
        
        return results
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get encode/decode stats: {str(e)}")
        return {}


def get_activity_log(user_id: int = None, limit: int = 50) -> list:
    """
    Get activity log entries.
    
    Args:
        user_id (int): Optional user ID filter
        limit (int): Number of records to retrieve
    
    Returns:
        list: Activity log entries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute("""
                SELECT id, user_id, action, details, created_at
                FROM activity_log
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT id, user_id, action, details, created_at
                FROM activity_log
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get activity log: {str(e)}")
        return []


def get_timeline_data(days: int = 7) -> list:
    """
    Get timeline data for operations over N days.
    
    Args:
        days (int): Number of days to retrieve
    
    Returns:
        list: Timeline data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM operations
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """, (days,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [{'date': str(row[0]), 'count': row[1]} for row in results]
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get timeline data: {str(e)}")
        return []


def get_size_distribution() -> dict:
    """
    Get distribution of message sizes.
    
    Returns:
        dict: Size distribution data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN message_size < 1000 THEN 'Small (< 1KB)'
                    WHEN message_size < 10000 THEN 'Medium (1-10KB)'
                    WHEN message_size < 100000 THEN 'Large (10-100KB)'
                    ELSE 'Very Large (> 100KB)'
                END as size_category,
                COUNT(*) as count
            FROM operations
            GROUP BY size_category
        """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {row[0]: row[1] for row in results}
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get size distribution: {str(e)}")
        return {}


def search_activity_log(search_term: str, limit: int = 50) -> list:
    """
    Search activity log by action or details.
    
    Args:
        search_term (str): Term to search for
        limit (int): Number of results to return
    
    Returns:
        list: Matching activity log entries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, action, details, created_at
            FROM activity_log
            WHERE action ILIKE %s OR details ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (f'%{search_term}%', f'%{search_term}%', limit))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except psycopg2.Error as e:
        logger.error(f"Failed to search activity log: {str(e)}")
        return []


def get_user_count() -> int:
    """Get total number of users."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except psycopg2.Error as e:
        logger.error(f"Failed to get user count: {str(e)}")
        return 0


def get_operation_count() -> int:
    """Get total number of operations."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM operations")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except psycopg2.Error as e:
        logger.error(f"Failed to get operation count: {str(e)}")
        return 0


def get_recent_activity(limit: int = 100) -> list:
    """
    Get recent activity entries.
    
    Args:
        limit (int): Number of recent entries to retrieve
    
    Returns:
        list: Recent activity entries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, user_id, action, details, created_at
            FROM activity_log
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get recent activity: {str(e)}")
        return []


def get_user_stats(username: str) -> list:
    """
    Get statistics for a specific user.
    
    Args:
        username (str): Username to get stats for
    
    Returns:
        list: List of (method, count) tuples
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First get user ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        
        if not user_result:
            cursor.close()
            conn.close()
            return []
        
        user_id = user_result[0]
        
        # Get method distribution for this user
        cursor.execute("""
            SELECT method, COUNT(*) as count
            FROM operations
            WHERE user_id = %s
            GROUP BY method
        """, (user_id,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results if results else []
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get user stats: {str(e)}")
        return []


def get_user_id(username: str) -> int:
    """
    Get user ID from username.
    
    Args:
        username (str): Username
    
    Returns:
        int: User ID or None if not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result[0] if result else None
        
    except psycopg2.Error as e:
        logger.error(f"Failed to get user ID: {str(e)}")
        return None