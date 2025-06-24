#!/usr/bin/env python3
"""
Script to fix the movies table structure by adding missing columns
"""

import mysql.connector
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

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

def check_movies_table_structure():
    """Check current movies table structure"""
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        # Get current table structure
        cursor.execute("DESCRIBE movies")
        columns = cursor.fetchall()
        
        print("Current movies table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        return [col[0] for col in columns]
        
    except Exception as e:
        print(f"Error checking table structure: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def add_missing_columns():
    """Add missing columns to movies table"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Define the expected columns and their definitions
        expected_columns = {
            'type': "ENUM('Movie', 'Series') NOT NULL DEFAULT 'Movie'",
            'trailer_url': "VARCHAR(255)",
            'audio_languages': "VARCHAR(255)",
            'uploaded_by': "INT",
            'created_at': "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
        
        # Get current columns
        cursor.execute("DESCRIBE movies")
        current_columns = [row[0] for row in cursor.fetchall()]
        
        print(f"Current columns: {current_columns}")
        
        # Add missing columns
        for column_name, column_def in expected_columns.items():
            if column_name not in current_columns:
                try:
                    sql = f"ALTER TABLE movies ADD COLUMN {column_name} {column_def}"
                    print(f"Adding column: {sql}")
                    cursor.execute(sql)
                    print(f"✓ Added column: {column_name}")
                except Exception as e:
                    print(f"✗ Error adding column {column_name}: {e}")
        
        # Add foreign key constraint for uploaded_by if it doesn't exist
        try:
            cursor.execute("""
                SELECT CONSTRAINT_NAME 
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME = 'movies' 
                AND COLUMN_NAME = 'uploaded_by' 
                AND REFERENCED_TABLE_NAME = 'users'
            """)
            fk_exists = cursor.fetchone()
            
            if not fk_exists:
                cursor.execute("""
                    ALTER TABLE movies 
                    ADD CONSTRAINT fk_movies_uploaded_by 
                    FOREIGN KEY (uploaded_by) REFERENCES users(id)
                """)
                print("✓ Added foreign key constraint for uploaded_by")
        except Exception as e:
            print(f"✗ Error adding foreign key: {e}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error adding columns: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    print("=== Movies Table Structure Fix ===")
    
    # Check current structure
    print("\n1. Checking current table structure...")
    current_columns = check_movies_table_structure()
    
    if current_columns is None:
        print("Failed to check table structure")
        return
    
    # Add missing columns
    print("\n2. Adding missing columns...")
    success = add_missing_columns()
    
    if success:
        print("\n3. Verifying final structure...")
        final_columns = check_movies_table_structure()
        
        if final_columns:
            print("\n✓ Movies table structure updated successfully!")
        else:
            print("\n✗ Failed to verify final structure")
    else:
        print("\n✗ Failed to add missing columns")

if __name__ == "__main__":
    main() 