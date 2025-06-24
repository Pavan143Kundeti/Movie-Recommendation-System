#!/usr/bin/env python3
"""
Script to check the users table structure
"""

import mysql.connector

# Database configuration
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com',
    'user': 'sql12786417',
    'password': 'm46Km6gKDb',
    'database': 'sql12786417'
}

def get_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def check_users_table():
    """Check users table structure"""
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        # Get current table structure
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        
        print("Current users table structure:")
        for column in columns:
            print(f"  {column[0]} - {column[1]}")
        
        # Get sample data to see what's actually there
        cursor.execute("SELECT * FROM users LIMIT 1")
        sample_data = cursor.fetchone()
        
        if sample_data:
            print(f"\nSample user data: {sample_data}")
        else:
            print("\nNo users found in table")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking users table: {e}")
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_users_table() 