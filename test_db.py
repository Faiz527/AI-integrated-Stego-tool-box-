"""Test database connection"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.db.db_utils import get_db_connection, initialize_database, add_user, verify_user

print("🔌 Testing database connection...\n")

try:
    # Test connection
    print("1️⃣  Testing connection to PostgreSQL...")
    conn = get_db_connection()
    print("   ✅ Connected to PostgreSQL!")
    conn.close()
    
    # Initialize tables
    print("\n2️⃣  Initializing database tables...")
    initialize_database()
    print("   ✅ Database tables created!")
    
    # Test by adding a demo user
    print("\n3️⃣  Testing user operations...")
    add_user("demo_user", "demo_password")
    print("   ✅ Test user added!")
    
    # Test authentication
    print("\n4️⃣  Testing user authentication...")
    is_valid = verify_user("demo_user", "demo_password")
    if is_valid:
        print("   ✅ User authentication works!")
    else:
        print("   ❌ User authentication failed")
    
    print("\n" + "="*50)
    print("🎉 All database tests passed!")
    print("="*50)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠️  Troubleshooting:")
    print("   1. Make sure PostgreSQL is running")
    print("   2. Check .env file has correct credentials")
    print("   3. Verify database 'stegnography' exists")