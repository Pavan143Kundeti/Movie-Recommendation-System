#!/usr/bin/env python3
"""
Script to check the activity_log table structure
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

def check_activity_log_table():
    """Check activity_log table structure"""
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'activity_log'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("activity_log table does not exist!")
            return
        
        # Get current table structure
        cursor.execute("DESCRIBE activity_log")
        columns = cursor.fetchall()
        
        print("Current activity_log table structure:")
        for column in columns:
            print(f"  {column[0]} - {column[1]}")
        
        # Get sample data to see what's actually there
        cursor.execute("SELECT * FROM activity_log LIMIT 1")
        sample_data = cursor.fetchone()
        
        if sample_data:
            print(f"\nSample activity_log data: {sample_data}")
        else:
            print("\nNo activity_log entries found in table")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking activity_log table: {e}")
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_activity_log_table() 