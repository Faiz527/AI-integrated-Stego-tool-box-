"""
Database Module
===============
Manages PostgreSQL database operations:
  - User management (registration, authentication)
  - Operation logging
  - Activity tracking
  - Analytics data queries
"""

from .db_utils import (
    get_db_connection,
    initialize_database,
    add_user,
    verify_user,
    log_operation,
    log_activity,
)

__all__ = [
    'get_db_connection',
    'initialize_database',
    'add_user',
    'verify_user',
    'get_user_id',
    'log_operation',
    'log_activity',
    'get_user_stats',
    'get_operation_stats',
    'get_timeline_data',
    'get_method_distribution',
    'get_recent_activity'
]
