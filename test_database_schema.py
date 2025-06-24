#!/usr/bin/env python3
"""
Test script to check database schema and debug ProgrammingError
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simulate Streamlit secrets
class MockSecrets:
    def __init__(self):
        self.mysql = {
            'host': 'sql12.freesqldatabase.com',
            'user': 'sql12786417',
            'password': 'm46Km6gKDb',
            'database': 'sql12786417'
        }
    
    def __getitem__(self, key):
        return getattr(self, key)

# Mock streamlit
import streamlit as st
st.secrets = MockSecrets()

print("🔍 Testing database schema...")

try:
    from modules import database
    
    # Run the diagnostic function
    database.diagnose_database()
    
    # Test a simple query to see what happens
    print("\n🔍 Testing simple SELECT query...")
    conn = database.get_conn()
    cursor = database.get_cursor(conn)
    
    try:
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        print(f"✅ Users table query successful: {result}")
    except Exception as e:
        print(f"❌ Users table query failed: {e}")
    
    try:
        cursor.execute("SELECT COUNT(*) as count FROM movies")
        result = cursor.fetchone()
        print(f"✅ Movies table query successful: {result}")
    except Exception as e:
        print(f"❌ Movies table query failed: {e}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Failed to test database schema: {e}")

print("\n🏁 Database schema test completed.") 