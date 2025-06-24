#!/usr/bin/env python3
"""
Test script to verify database connection works with fallback connectors
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules import database
    print("✅ Successfully imported database module")
    
    # Test connection
    try:
        conn = database.get_conn()
        print("✅ Database connection successful")
        
        # Test a simple query
        cursor = database.get_cursor(conn)
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"✅ Test query successful: {result}")
        
        cursor.close()
        conn.close()
        print("✅ Connection closed successfully")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        
except Exception as e:
    print(f"❌ Failed to import database module: {e}")
    print("This might be due to missing dependencies or configuration issues.") 