import mysql.connector

def test_mysql_connection():
    """Test MySQL connection and create database"""
    try:
        # Try to connect without specifying database
        print("Testing MySQL connection...")
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pavan@3048"
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL!")
            
            cursor = connection.cursor()
            
            # Create database
            print("Creating database 'movie_db'...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS movie_db")
            print("✅ Database 'movie_db' created/verified!")
            
            # Switch to the database
            cursor.execute("USE movie_db")
            print("✅ Switched to 'movie_db' database!")
            
            # Check if tables exist
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Found {len(tables)} tables in the database")
            
            cursor.close()
            connection.close()
            return True
            
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        return False

if __name__ == "__main__":
    test_mysql_connection() 