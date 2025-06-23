import mysql.connector
import streamlit as st

def add_database_indexes():
    """Add database indexes for better performance"""
    
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        cursor = connection.cursor()
        
        print("🔧 Adding database indexes...")
        
        # List of indexes to create
        indexes = [
            ("idx_movies_title", "movies", "title"),
            ("idx_movies_genre", "movies", "genre"),
            ("idx_activity_log_user_id", "activity_log", "user_id"),
            ("idx_activity_log_created_at", "activity_log", "created_at"),
            ("idx_click_events_user_id", "click_events", "user_id"),
            ("idx_click_events_movie_id", "click_events", "movie_id")
        ]
        
        for index_name, table_name, column_name in indexes:
            try:
                cursor.execute(f"CREATE INDEX {index_name} ON {table_name}({column_name})")
                print(f"✅ Created index {index_name}")
            except mysql.connector.Error as e:
                if "Duplicate key name" in str(e):
                    print(f"ℹ️ Index {index_name} already exists")
                else:
                    print(f"⚠️ Error creating {index_name}: {e}")
        
        connection.commit()
        print("🎉 Database indexes added successfully!")
        
    except mysql.connector.Error as e:
        print(f"❌ Database connection error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    try:
        import toml
        with open('.streamlit/secrets.toml', 'r') as f:
            st.secrets = toml.load(f)
        add_database_indexes()
    except FileNotFoundError:
        print("❌ Please create .streamlit/secrets.toml file with your MySQL credentials")
    except Exception as e:
        print(f"❌ Error: {e}") 