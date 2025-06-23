import mysql.connector
import streamlit as st

def fix_database_schema():
    """Upgrade database schema for advanced features"""
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        cursor = connection.cursor()
        print("🔧 Upgrading database schema for advanced features...")

        # Follows table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS follows (
                id INT AUTO_INCREMENT PRIMARY KEY,
                follower_id INT NOT NULL,
                following_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_follow (follower_id, following_id)
            )
        """)
        print("✅ follows table ready")

        # Ratings & Reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings_reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                movie_id INT NOT NULL,
                rating INT CHECK (rating >= 1 AND rating <= 5),
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
                UNIQUE KEY unique_rating (user_id, movie_id)
            )
        """)
        print("✅ ratings_reviews table ready")

        # Comments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                movie_id INT NOT NULL,
                text VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
            )
        """)
        print("✅ comments table ready")

        # Reminders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                movie_id INT NOT NULL,
                remind_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
            )
        """)
        print("✅ reminders table ready")

        # Search history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                keyword VARCHAR(255) NOT NULL,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("✅ search_history table ready")

        # A/B tests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ab_tests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                group_name VARCHAR(50) NOT NULL,
                feature VARCHAR(50) NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("✅ ab_tests table ready")

        # Patch: Add status column to history if missing
        try:
            cursor.execute("SHOW COLUMNS FROM history LIKE 'status'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE history ADD COLUMN status ENUM('watched', 'completed') DEFAULT 'watched' AFTER movie_id")
                print("✅ Added status column to history table")
            else:
                print("ℹ️ status column already exists in history table")
        except mysql.connector.Error as e:
            print(f"⚠️ Error patching history table: {e}")

        connection.commit()
        print("🎉 Advanced schema upgrade complete!")
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    try:
        import toml
        with open('.streamlit/secrets.toml', 'r') as f:
            st.secrets = toml.load(f)
        fix_database_schema()
    except FileNotFoundError:
        print("❌ Please create .streamlit/secrets.toml file with your MySQL credentials")
    except Exception as e:
        print(f"❌ Error: {e}") 