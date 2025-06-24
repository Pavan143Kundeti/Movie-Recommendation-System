#!/usr/bin/env python3
"""
Test script to debug MySQL connector imports
"""

print("Testing MySQL connector imports...")

# Test mysql.connector
try:
    import mysql.connector
    from mysql.connector import pooling
    print("✅ mysql.connector imported successfully")
    print(f"   Version: {mysql.connector.__version__}")
    MYSQL_AVAILABLE = True
except ImportError as e:
    print(f"❌ mysql.connector import failed: {e}")
    MYSQL_AVAILABLE = False

# Test PyMySQL
try:
    import pymysql
    import pymysql.cursors
    print("✅ PyMySQL imported successfully")
    print(f"   Version: {pymysql.__version__}")
    PYMySQL_AVAILABLE = True
except ImportError as e:
    print(f"❌ PyMySQL import failed: {e}")
    PYMySQL_AVAILABLE = False

print(f"\nSummary:")
print(f"mysql.connector available: {MYSQL_AVAILABLE}")
print(f"PyMySQL available: {PYMySQL_AVAILABLE}")

# Test the exact same logic as in database.py
print(f"\nTesting database.py logic:")
if MYSQL_AVAILABLE:
    print("✅ Would use mysql.connector")
elif PYMySQL_AVAILABLE:
    print("✅ Would use PyMySQL")
else:
    print("❌ No connectors available")

# Test importing the database module
print(f"\nTesting database module import:")
try:
    from modules import database
    print("✅ Database module imported successfully")
    
    # Check the flags
    print(f"   database.MYSQL_AVAILABLE: {getattr(database, 'MYSQL_AVAILABLE', 'Not found')}")
    print(f"   database.PYMySQL_AVAILABLE: {getattr(database, 'PYMySQL_AVAILABLE', 'Not found')}")
    
except Exception as e:
    print(f"❌ Database module import failed: {e}") 