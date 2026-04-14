"""
Database Module
===============
Manages PostgreSQL database operations:
  - User management (registration, authentication)
  - Activity tracking
"""

from .db_utils import (
    get_db_connection,
    initialize_database,
    add_user,
    verify_user,
    log_activity,
)

# Import create_db for convenience
from . import create_db

__all__ = [
    'get_db_connection',
    'initialize_database',
    'add_user',
    'verify_user',
    'log_activity',
    'create_db',
]
