#!/usr/bin/env python3
"""
Comprehensive database connection test for Streamlit app
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

# Mock streamlit
import streamlit as st
st.secrets = MockSecrets()

print("🔍 Testing database connection with exact app configuration...")

try:
    from modules import database
    print("✅ Database module imported successfully")
    
    # Test the exact same logic as in the app
    print("\n🔍 Testing connection pool creation...")
    if hasattr(database, 'connection_pool'):
        print(f"   Connection pool: {database.connection_pool}")
    else:
        print("   No connection pool found")
    
    print("\n🔍 Testing get_conn() function...")
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
        print(f"   Error type: {type(e).__name__}")
        
        # Test individual connectors
        print("\n🔍 Testing individual connectors...")
        
        # Test mysql.connector directly
        try:
            import mysql.connector
            print("✅ mysql.connector import successful")
            
            # Test direct connection
            direct_conn = mysql.connector.connect(
                host=st.secrets.mysql['host'],
                user=st.secrets.mysql['user'],
                password=st.secrets.mysql['password'],
                database=st.secrets.mysql['database']
            )
            print("✅ Direct mysql.connector connection successful")
            direct_conn.close()
            
        except Exception as e:
            print(f"❌ Direct mysql.connector connection failed: {e}")
        
        # Test PyMySQL directly
        try:
            import pymysql
            print("✅ PyMySQL import successful")
            
            # Test direct connection
            direct_conn = pymysql.connect(
                host=st.secrets.mysql['host'],
                user=st.secrets.mysql['user'],
                password=st.secrets.mysql['password'],
                database=st.secrets.mysql['database'],
                charset='utf8mb4'
            )
            print("✅ Direct PyMySQL connection successful")
            direct_conn.close()
            
        except Exception as e:
            print(f"❌ Direct PyMySQL connection failed: {e}")
    
    # Test the specific function that's failing
    print("\n🔍 Testing get_movie_filter_bounds() function...")
    try:
        filter_data = database.get_movie_filter_bounds()
        print(f"✅ get_movie_filter_bounds() successful: {filter_data}")
    except Exception as e:
        print(f"❌ get_movie_filter_bounds() failed: {e}")
        
except Exception as e:
    print(f"❌ Failed to import or test database module: {e}")
    print("This might be due to missing dependencies or configuration issues.")

print("\n🏁 Database connection test completed.") 