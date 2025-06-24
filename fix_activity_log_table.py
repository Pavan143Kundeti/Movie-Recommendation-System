#!/usr/bin/env python3
"""
Script to fix the activity_log table by adding the missing 'details' column
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

def fix_activity_log_table():
    """Fix activity_log table by adding missing columns"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'activity_log'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating activity_log table...")
            cursor.execute("""
                CREATE TABLE activity_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action VARCHAR(255),
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            print("✅ activity_log table created successfully!")
        else:
            # Check current structure
            cursor.execute("DESCRIBE activity_log")
            columns = [col[0] for col in cursor.fetchall()]
            print(f"Current activity_log columns: {columns}")
            
            # Add missing columns
            if 'details' not in columns:
                print("Adding 'details' column...")
                cursor.execute("ALTER TABLE activity_log ADD COLUMN details TEXT")
                print("✅ 'details' column added successfully!")
            
            # Don't add created_at if timestamp already exists
            if 'created_at' not in columns and 'timestamp' not in columns:
                print("Adding 'created_at' column...")
                cursor.execute("ALTER TABLE activity_log ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                print("✅ 'created_at' column added successfully!")
            elif 'timestamp' in columns:
                print("✅ 'timestamp' column already exists, skipping 'created_at'")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error fixing activity_log table: {e}")
        cursor.close()
        conn.close()
        return False

if __name__ == "__main__":
    print("Fixing activity_log table...")
    if fix_activity_log_table():
        print("✅ activity_log table fixed successfully!")
    else:
        print("❌ Failed to fix activity_log table!") 