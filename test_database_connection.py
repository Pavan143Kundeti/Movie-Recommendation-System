#!/usr/bin/env python3
"""
Test script to verify database connection and imports
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing database connection...")

# Test imports
try:
    import mysql.connector
    print("✅ mysql.connector imported successfully")
except ImportError as e:
    print(f"❌ mysql.connector import failed: {e}")

try:
    import pymysql
    print("✅ pymysql imported successfully")
except ImportError as e:
    print(f"❌ pymysql import failed: {e}")

# Test database module import
try:
    import modules.database as database
    print("✅ database module imported successfully")
except ImportError as e:
    print(f"❌ database module import failed: {e}")

# Test database connection
try:
    conn = database.get_conn()
    print("✅ Database connection successful")
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# Test getting filter data
try:
    filter_data = database.get_movie_filter_bounds()
    print(f"✅ Filter data retrieved: {filter_data}")
except Exception as e:
    print(f"❌ Filter data retrieval failed: {e}")

print("Test completed!") 