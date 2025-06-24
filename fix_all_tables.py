#!/usr/bin/env python3
"""
Script to fix all database table structures by adding missing columns
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

def check_table_structure(table_name):
    """Check current table structure"""
    conn = get_connection()
    if not conn:
        return None
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        print(f"Current {table_name} table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        return [col[0] for col in columns]
        
    except Exception as e:
        print(f"Error checking {table_name} table structure: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def fix_movies_table():
    """Fix movies table structure"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Define the expected columns and their definitions
        expected_columns = {
            'release_year': "INT",
            'cast': "TEXT"
        }
        
        # Get current columns
        cursor.execute("DESCRIBE movies")
        current_columns = [row[0] for row in cursor.fetchall()]
        
        print(f"Current movies columns: {current_columns}")
        
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
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error fixing movies table: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def fix_history_table():
    """Fix history table structure"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if history table exists
        cursor.execute("SHOW TABLES LIKE 'history'")
        if not cursor.fetchone():
            print("History table doesn't exist, creating it...")
            cursor.execute("""
                CREATE TABLE history (
                    user_id INT,
                    movie_id INT,
                    status VARCHAR(50) DEFAULT 'watched',
                    watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, movie_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (movie_id) REFERENCES movies(id)
                )
            """)
            print("✓ Created history table")
        else:
            # Check if status column exists
            cursor.execute("DESCRIBE history")
            columns = [row[0] for row in cursor.fetchall()]
            
            if 'status' not in columns:
                try:
                    cursor.execute("ALTER TABLE history ADD COLUMN status VARCHAR(50) DEFAULT 'watched'")
                    print("✓ Added status column to history table")
                except Exception as e:
                    print(f"✗ Error adding status column: {e}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error fixing history table: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def fix_watchlist_table():
    """Fix watchlist table structure"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if watchlist table exists
        cursor.execute("SHOW TABLES LIKE 'watchlist'")
        if not cursor.fetchone():
            print("Watchlist table doesn't exist, creating it...")
            cursor.execute("""
                CREATE TABLE watchlist (
                    user_id INT,
                    movie_id INT,
                    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, movie_id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (movie_id) REFERENCES movies(id)
                )
            """)
            print("✓ Created watchlist table")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error fixing watchlist table: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def fix_ratings_table():
    """Fix ratings table structure"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if ratings table exists
        cursor.execute("SHOW TABLES LIKE 'ratings'")
        if not cursor.fetchone():
            print("Ratings table doesn't exist, creating it...")
            cursor.execute("""
                CREATE TABLE ratings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    movie_id INT NOT NULL,
                    rating INT CHECK (rating BETWEEN 1 AND 5),
                    review TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_movie_rating (user_id, movie_id)
                )
            """)
            print("✓ Created ratings table")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Error fixing ratings table: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    print("=== Database Schema Fix ===")
    
    # Fix movies table
    print("\n1. Fixing movies table...")
    check_table_structure('movies')
    success = fix_movies_table()
    if success:
        print("\n2. Verifying movies table...")
        check_table_structure('movies')
    
    # Fix history table
    print("\n3. Fixing history table...")
    success = fix_history_table()
    if success:
        print("\n4. Verifying history table...")
        check_table_structure('history')
    
    # Fix watchlist table
    print("\n5. Fixing watchlist table...")
    success = fix_watchlist_table()
    if success:
        print("\n6. Verifying watchlist table...")
        check_table_structure('watchlist')
    
    # Fix ratings table
    print("\n7. Fixing ratings table...")
    success = fix_ratings_table()
    if success:
        print("\n8. Verifying ratings table...")
        check_table_structure('ratings')
    
    print("\n✓ Database schema fix completed!")

if __name__ == "__main__":
    main() 