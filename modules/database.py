import streamlit as st
import hashlib
import pandas as pd
from datetime import datetime, timedelta
import random
import json
import re
import os

# --- Robust MySQL import for error handling ---
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    mysql = None
    MYSQL_AVAILABLE = False

try:
    import pymysql
    PYMySQL_AVAILABLE = True
except ImportError:
    pymysql = None
    PYMySQL_AVAILABLE = False

# --- Database Connection Config ---
DB_CONFIG = {
    'host': st.secrets["mysql"]["host"],
    'database': st.secrets["mysql"]["database"],
    'user': st.secrets["mysql"]["user"],
    'password': st.secrets["mysql"]["password"]
}

def get_conn():
    """Get database connection with fallback logic."""
    # Try mysql.connector first
    if MYSQL_AVAILABLE and mysql is not None:
        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database']
            )
            print("✅ Connected using mysql.connector")
            return conn
        except Exception as e:
            print(f"⚠️  mysql.connector connection failed: {e}")
    
    # Try PyMySQL as fallback
    if PYMySQL_AVAILABLE and pymysql is not None:
        try:
            conn = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset='utf8mb4'
            )
            print("✅ Connected using PyMySQL")
            return conn
        except Exception as e:
            print(f"⚠️  PyMySQL connection failed: {e}")
    
    # If we get here, no connector worked
    error_msg = "No database connector available. "
    if not MYSQL_AVAILABLE and not PYMySQL_AVAILABLE:
        error_msg += "Please install mysql-connector-python or PyMySQL."
    else:
        error_msg += "Database connection failed. Please check your credentials."
    
    st.error(error_msg)
    raise Exception("No database connector available")

def get_cursor(conn):
    # Try to get a dictionary cursor if possible
    try:
        return conn.cursor(dictionary=True)
    except Exception:
        return conn.cursor()

def diagnose_database():
    """Diagnostic function to check database schema and tables."""
    try:
        conn = get_conn()
        cursor = get_cursor(conn)
        
        print("🔍 Database Diagnosis:")
        
        # Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        if cursor.fetchone():
            print("✅ users table exists")
            
            # Check users table structure
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            print("📋 users table columns:")
            for col in columns:
                # Handle both tuple and dict formats
                if isinstance(col, dict):
                    print(f"   - {col['Field']} ({col['Type']})")
                else:
                    print(f"   - {col[0]} ({col[1]})")
        else:
            print("❌ users table does not exist")
            
        # Check if movies table exists
        cursor.execute("SHOW TABLES LIKE 'movies'")
        if cursor.fetchone():
            print("✅ movies table exists")
        else:
            print("❌ movies table does not exist")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database diagnosis failed: {e}")
        print(f"   Error type: {type(e).__name__}")

# --- Table Creation (run once, or check/auto-create) ---
CREATE_TABLES_SQL = [
    '''CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        phone_number VARCHAR(20),
        is_verified BOOLEAN DEFAULT FALSE,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE IF NOT EXISTS movies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        genre VARCHAR(100),
        type VARCHAR(20),
        release_year INT,
        description TEXT,
        cast TEXT,
        poster_url VARCHAR(500),
        trailer_url VARCHAR(500),
        audio_languages VARCHAR(100),
        uploaded_by INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (uploaded_by) REFERENCES users(id)
    )''',
    '''CREATE TABLE IF NOT EXISTS ratings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        movie_id INT,
        rating INT CHECK (rating >= 1 AND rating <= 5),
        review TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_rating (user_id, movie_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (movie_id) REFERENCES movies(id)
    )''',
    '''CREATE TABLE IF NOT EXISTS watchlist (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        movie_id INT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY unique_watchlist (user_id, movie_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (movie_id) REFERENCES movies(id)
    )''',
    '''CREATE TABLE IF NOT EXISTS history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        movie_id INT,
        watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (movie_id) REFERENCES movies(id)
    )'''
]

def auto_migrate_users_table():
    """Automatically add missing columns to the users table if they do not exist."""
    required_columns = {
        'full_name': "VARCHAR(255) DEFAULT NULL",
        'date_joined': "DATETIME DEFAULT CURRENT_TIMESTAMP",
        'last_login': "DATETIME DEFAULT NULL",
        'profile_pic': "VARCHAR(512) DEFAULT NULL",
        'bio': "TEXT DEFAULT NULL",
        'favorite_genres': "VARCHAR(255) DEFAULT NULL",
        'is_admin': "BOOLEAN NOT NULL DEFAULT FALSE"
    }
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute("SHOW COLUMNS FROM users")
        existing_columns = set(row[0] for row in cursor.fetchall())
        for col, col_def in required_columns.items():
            if col not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_def}")
                    print(f"[MIGRATION] Added missing column: {col}")
                except Exception as e:
                    print(f"[MIGRATION] Error adding column {col}: {e}")
        conn.commit()
    except Exception as e:
        print(f"[MIGRATION] Error checking/updating users table: {e}")
    finally:
        cursor.close()
        conn.close()

def init_database():
    auto_migrate_users_table()
    conn = get_conn()
    cursor = get_cursor(conn)

    # SQL commands to create tables
    commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            phone_number VARCHAR(20) NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            type ENUM('Movie', 'Series') NOT NULL,
            genre VARCHAR(100),
            description TEXT,
            release_year INT,
            cast TEXT,
            poster_url TEXT,
            trailer_url VARCHAR(255),
            audio_languages VARCHAR(255),
            uploaded_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS watchlist (
            user_id INT,
            movie_id INT,
            added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS history (
            user_id INT,
            movie_id INT,
            watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ratings (
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
        """,
        """
        CREATE TABLE IF NOT EXISTS activity_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            action VARCHAR(255),
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS watch_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            movie_id INT,
            started_at TIMESTAMP,
            ended_at TIMESTAMP NULL,
            duration_minutes INT DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
        )
        """
    ]

    # Execute each command
    for command in commands:
        try:
            cursor.execute(command)
        except Exception as err:
            st.error(f"Error creating table: {err}")

    conn.commit()
    cursor.close()
    conn.close()
    st.success("Database tables checked and created successfully!")

# --- User Management Functions ---
def add_user(username, email, password_hash, phone=None, is_admin=False):
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        # Use role column instead of is_admin column
        role = 'admin' if is_admin else 'user'
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, phone_number, role) VALUES (%s, %s, %s, %s, %s)",
            (username, email, password_hash, phone, role)
        )
        conn.commit()
        return True
    except Exception as e:
        print("[DB] add_user error:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_by_email(email):
    conn = get_conn()
    cursor = get_cursor(conn)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_user_by_username(username):
    """Return user row by username, or None if not found."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        return row
    except Exception as e:
        print(f"[DB] get_user_by_username error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# Add more user, movie, rating, watchlist, and history functions as needed...

# --- PASSWORD HASHING ---

def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- TABLE CREATION ---

def create_tables():
    """
    Creates all the necessary tables in the database if they do not already exist.
    This function should be run once at the start of the application.
    """
    conn = get_conn()
    cursor = get_cursor(conn)

    # SQL commands to create tables
    commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            phone_number VARCHAR(20) NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            type ENUM('Movie', 'Series') NOT NULL,
            genre VARCHAR(100),
            description TEXT,
            release_year INT,
            cast TEXT,
            poster_url TEXT,
            trailer_url VARCHAR(255),
            audio_languages VARCHAR(255),
            uploaded_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS watchlist (
            user_id INT,
            movie_id INT,
            added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS history (
            user_id INT,
            movie_id INT,
            watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ratings (
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
        """,
        """
        CREATE TABLE IF NOT EXISTS activity_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            action VARCHAR(255),
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS watch_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            movie_id INT,
            started_at TIMESTAMP,
            ended_at TIMESTAMP NULL,
            duration_minutes INT DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
        )
        """
    ]

    # Execute each command
    for command in commands:
        try:
            cursor.execute(command)
        except Exception as err:
            st.error(f"Error creating table: {err}")

    conn.commit()
    cursor.close()
    conn.close()
    st.success("Database tables checked and created successfully!")

# --- ACTIVITY LOGGING ---

def log_activity(user_id, action, details=""):
    """Logs user activity to the activity_log table."""
    conn = get_conn()
    cursor = get_cursor(conn)
    
    try:
        cursor.execute(
            "INSERT INTO activity_log (user_id, action, details) VALUES (%s, %s, %s)",
            (user_id, action, details)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error logging activity: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_activity(user_id, limit=5):
    """Retrieves recent activity for a user."""
    conn = get_conn()
    cursor = get_cursor(conn)
    
    try:
        cursor.execute("""
            SELECT action, details, created_at 
            FROM activity_log 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """, (user_id, limit))
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching activity: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- DASHBOARD METRICS ---

def get_dashboard_metrics():
    """Fetches various metrics for the admin dashboard."""
    conn = get_conn()
    cursor = get_cursor(conn)
    metrics = {
        'total_users': 0,
        'total_movies': 0,
        'total_watchlist': 0,
        'total_watched': 0,
        'movies_by_genre': [],
        'recent_uploads': [],
        'recent_activity': 0,
        'avg_watch_time': 0
    }

    try:
        # Total users
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        result = cursor.fetchone()
        if result: metrics['total_users'] = result['total_users']

        # Total movies
        cursor.execute("SELECT COUNT(*) as total_movies FROM movies")
        result = cursor.fetchone()
        if result: metrics['total_movies'] = result['total_movies']

        # Total watchlist items
        cursor.execute("SELECT COUNT(*) as total_watchlist FROM watchlist")
        result = cursor.fetchone()
        if result: metrics['total_watchlist'] = result['total_watchlist']

        # Total watched movies (history)
        cursor.execute("SELECT COUNT(*) as total_watched FROM history")
        result = cursor.fetchone()
        if result: metrics['total_watched'] = result['total_watched']

        # Movies by genre
        cursor.execute("SELECT genre, COUNT(*) as count FROM movies WHERE genre IS NOT NULL AND genre != '' GROUP BY genre ORDER BY count DESC")
        result = cursor.fetchall()
        if result: metrics['movies_by_genre'] = result

        # Recent uploads
        cursor.execute("SELECT title, created_at FROM movies ORDER BY created_at DESC LIMIT 5")
        result = cursor.fetchall()
        if result: metrics['recent_uploads'] = result
        
        # Recent activity count (log entries in the last 7 days)
        cursor.execute("SELECT COUNT(*) as activity_count FROM activity_log WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
        result = cursor.fetchone()
        if result: metrics['recent_activity'] = result['activity_count']

        # Average watch time per user
        cursor.execute("SELECT AVG(duration_minutes) as avg_watch FROM watch_sessions WHERE duration_minutes > 0")
        result = cursor.fetchone()
        if result and result.get('avg_watch') is not None:
            metrics['avg_watch_time'] = round(result['avg_watch'], 2)

    except Exception as e:
        print(f"Error fetching dashboard metrics: {e}")
    finally:
        cursor.close()
        conn.close()

    return metrics

# --- NEW ADVANCED DASHBOARD ---
def get_advanced_dashboard_metrics():
    """Fetches a comprehensive set of metrics for the advanced admin dashboard."""
    try:
        conn = get_conn()
        cursor = get_cursor(conn)
        metrics = {}
        # Example: total users
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        row = cursor.fetchone()
        if row and isinstance(row, dict):
            metrics['total_users'] = row.get('total_users', 0)
        else:
            metrics['total_users'] = 0
        # Add more metrics as needed...
        cursor.close()
        conn.close()
        return metrics
    except Exception as e:
        import streamlit as st
        st.error(f"Dashboard metrics error: {e}")
        print(f"[Dashboard Metrics Error] {e}")
        return {}

def manually_verify_user(user_id):
    """Manually marks a user as verified by an admin."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute("UPDATE users SET is_verified = 1 WHERE id = %s", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error manually verifying user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def reset_user_password_by_admin(user_id, new_password):
    """Resets a user's password by an admin."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed_password, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error resetting password by admin: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- SEARCH AUTOCOMPLETE ---

def get_movie_suggestions(query, limit=10):
    """Gets movie title suggestions for autocomplete."""
    conn = get_conn()
    cursor = get_cursor(conn)
    
    try:
        cursor.execute("""
            SELECT title, genre, release_year 
            FROM movies 
            WHERE title LIKE %s 
            ORDER BY release_year DESC 
            LIMIT %s
        """, (f"%{query}%", limit))
        return cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching suggestions: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- BULK UPLOAD ---

def bulk_upload_movies(csv_data, uploaded_by):
    """
    Bulk upload movies from a pandas DataFrame.
    This function is more robust, validates data, and uses executemany for efficiency.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    
    # List to hold movie data tuples for insertion
    movies_to_insert = []
    # List to hold detailed error messages
    errors = []
    success_count = 0

    required_columns = ['title', 'type', 'genre', 'release_year', 'description', 'cast', 'poster_url', 'trailer_url']
    
    # Normalize column names (e.g., "Title " -> "title")
    csv_data.columns = csv_data.columns.str.strip().str.lower()

    for index, row in csv_data.iterrows():
        try:
            # --- Data Validation and Cleaning ---
            title = str(row['title']).strip()
            if not title:
                errors.append(f"Row {index + 2}: 'title' cannot be empty.")
                continue

            # Ensure 'type' is either 'Movie' or 'Series', default to 'Movie'
            item_type = str(row.get('type', 'Movie')).strip().capitalize()
            if item_type not in ['Movie', 'Series']:
                item_type = 'Movie'

            # Safely convert release_year to integer
            try:
                release_year = int(row.get('release_year')) if pd.notna(row.get('release_year')) else None
            except (ValueError, TypeError):
                errors.append(f"Row {index + 2}: Invalid 'release_year' for title '{title}'. Must be a whole number.")
                continue

            # Prepare a tuple with all the data for insertion
            movie_data = (
                title,
                item_type,
                str(row.get('genre', '')).strip(),
                release_year,
                str(row.get('description', '')).strip(),
                str(row.get('cast', '')).strip(),
                str(row.get('poster_url', '')).strip(),
                str(row.get('trailer_url', '')).strip(),
                uploaded_by
            )
            movies_to_insert.append(movie_data)

        except KeyError as e:
            errors.append(f"Row {index + 2}: Missing required column: {e}. Please check the CSV file.")
        except Exception as e:
            errors.append(f"Row {index + 2}: An unexpected error occurred for title '{row.get('title', 'N/A')}': {e}")

    # --- Bulk Insert into Database ---
    if not movies_to_insert:
        error_message = "No valid movies to upload. Please check the errors below."
        if errors:
            error_message += "\\n" + "\\n".join(errors)
        return False, error_message

    try:
        sql = """
            INSERT INTO movies (title, type, genre, release_year, description, cast, poster_url, trailer_url, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                genre=VALUES(genre), description=VALUES(description), cast=VALUES(cast),
                poster_url=VALUES(poster_url), trailer_url=VALUES(trailer_url);
        """
        cursor.executemany(sql, movies_to_insert)
        conn.commit()
        success_count = cursor.rowcount
        
        # Log the bulk upload activity
        log_activity(uploaded_by, "bulk_upload", f"Attempted to upload {len(csv_data)} movies. Succeeded: {success_count}. Failed: {len(errors)}.")

        # Prepare final message
        message = f"Successfully processed {success_count} movie(s)."
        if errors:
            message += f"\\n\\nEncountered {len(errors)} error(s):\\n- " + "\\n- ".join(errors)
        
        return True, message

    except Exception as e:
        conn.rollback()
        return False, f"A database error occurred: {e}"
    finally:
        cursor.close()
        conn.close()

# --- PAGINATION ---

def get_movie_filter_bounds():
    """Gets the min/max year and distinct genres/languages for filter widgets."""
    conn = get_conn()
    cursor = get_cursor(conn)
    bounds = {
        'min_year': 1900,
        'max_year': datetime.now().year,
        'genres': [],
        'audio_languages': []
    }
    try:
        cursor.execute("SELECT MIN(release_year) as min_y, MAX(release_year) as max_y FROM movies WHERE release_year > 1880")
        year_res = cursor.fetchone()
        if year_res and year_res['min_y']:
            bounds['min_year'] = year_res['min_y']
            bounds['max_year'] = year_res['max_y']

        cursor.execute("SELECT DISTINCT genre FROM movies WHERE genre IS NOT NULL AND genre != ''")
        genres_res = cursor.fetchall()
        if genres_res:
            genres = set()
            for row in genres_res:
                genres.update(g.strip() for g in row['genre'].split(','))
            bounds['genres'] = sorted(list(genres))
        
        cursor.execute("SELECT DISTINCT audio_languages FROM movies WHERE audio_languages IS NOT NULL AND audio_languages != ''")
        lang_res = cursor.fetchall()
        if lang_res:
            languages = set()
            for row in lang_res:
                languages.update(lang.strip() for lang in row['audio_languages'].split(','))
            bounds['audio_languages'] = sorted(list(languages))

    except Exception as err:
        print(f"Error getting filter bounds: {err}")
    finally:
        cursor.close()
        conn.close()
    return bounds

def get_movies_paginated(page=1, per_page=12, query=None, movie_type=None, genres=None, year_range=None, rating_filter=None, audio_languages=None, sort_by='popularity'):
    """
    Gets movies with pagination and advanced filtering.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    params = []
    
    # Base query now includes a LEFT JOIN to calculate average rating
    base_query = """
        FROM movies m
        LEFT JOIN (SELECT movie_id, AVG(rating) as avg_rating FROM reviews GROUP BY movie_id) r
        ON m.id = r.movie_id
        WHERE 1=1
    """
    
    # --- DYNAMIC WHERE CLAUSES ---
    where_clauses = []

    if query:
        where_clauses.append("(m.title LIKE %s OR m.description LIKE %s OR m.cast LIKE %s)")
        term = f"%{query}%"
        params.extend([term, term, term])
    
    if movie_type:
        where_clauses.append("m.type = %s")
        params.append(movie_type)

    if genres:
        genre_placeholders = " OR ".join(["FIND_IN_SET(%s, m.genre) > 0"] * len(genres))
        where_clauses.append(f"({genre_placeholders})")
        params.extend(genres)

    if year_range:
        where_clauses.append("m.release_year BETWEEN %s AND %s")
        params.extend(year_range)
    
    if audio_languages:
        lang_placeholders = " OR ".join(["FIND_IN_SET(%s, m.audio_languages) > 0"] * len(audio_languages))
        where_clauses.append(f"({lang_placeholders})")
        params.extend(audio_languages)
        
    where_sql = " AND ".join(where_clauses) if where_clauses else ""
    full_where_sql = base_query + (" AND " + where_sql if where_sql else "")

    # --- DYNAMIC HAVING CLAUSE FOR RATING ---
    having_sql = ""
    if rating_filter:
        if rating_filter == "4+":
            having_sql = " HAVING avg_rating >= 4"
        elif rating_filter == "3+":
            having_sql = " HAVING avg_rating >= 3"
        elif rating_filter == "<3":
            having_sql = " HAVING avg_rating < 3"

    # --- DYNAMIC ORDER BY CLAUSE ---
    order_by_sql = " ORDER BY CASE WHEN m.poster_url IS NOT NULL AND TRIM(m.poster_url) <> '' THEN 0 ELSE 1 END, "
    if sort_by == 'rating':
        order_by_sql += "avg_rating DESC, m.id"
    elif sort_by == 'year':
        order_by_sql += "m.release_year DESC, m.id"
    else: # Default to popularity (e.g., movie id as a proxy)
        order_by_sql += "m.id DESC"

    # --- COUNT QUERY ---
    count_sql = f"SELECT COUNT(DISTINCT m.id) as total {full_where_sql}"
    # The HAVING clause needs to be applied to the count as well
    if having_sql:
        # This is a bit tricky; we need to count from a subquery
        count_sql = f"SELECT COUNT(*) as total FROM (SELECT m.id, MAX(r.avg_rating) as avg_rating {full_where_sql} GROUP BY m.id {having_sql}) as sub"

    try:
        cursor.execute(count_sql, params)
        result = cursor.fetchone()
        total_movies = result['total'] if result else 0
    except Exception as err:
        print(f"Error counting movies: {err}")
        return [], 0

    # --- DATA QUERY ---
    pagination_sql = " LIMIT %s OFFSET %s"
    offset = (page - 1) * per_page
    
    select_sql = f"""
        SELECT m.*, MAX(r.avg_rating) as avg_rating
        {full_where_sql}
        GROUP BY m.id
        {having_sql}
        {order_by_sql}
        {pagination_sql}
    """
    
    try:
        cursor.execute(select_sql, params + [per_page, offset])
        movies = cursor.fetchall()
        return movies, total_movies
    except Exception as err:
        print(f"Error fetching paginated movies: {err}")
        return [], 0
    finally:
        cursor.close()
        conn.close()

# --- USER AUTHENTICATION FUNCTIONS ---

def update_last_login(user_id):
    """Update the last_login field for a user to the current timestamp."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        # Check if last_login column exists before trying to update it
        cursor.execute("SHOW COLUMNS FROM users LIKE 'last_login'")
        if cursor.fetchone():
            cursor.execute("UPDATE users SET last_login=NOW() WHERE id = %s", (user_id,))
            conn.commit()
        else:
            print("[AUTH_DEBUG] last_login column does not exist in users table")
    except Exception as e:
        print(f"[AUTH_DEBUG] Failed to update last_login: {e}")
    finally:
        cursor.close()
        conn.close()

def authenticate_user(username_or_email, password):
    """Authenticate a user by username or email."""
    print(f"[AUTH_DEBUG] Attempting to authenticate user: {username_or_email}")
    password_hash = hash_password(password)
    print(f"[AUTH_DEBUG] Hashed input password to: {password_hash}")

    try:
        conn = get_conn()
        cursor = get_cursor(conn)
        
        # Check if the input is likely an email address
        is_email = re.match(r"[^@]+@[^@]+\.[^@]+", username_or_email)
        
        # Fetch only the columns that actually exist in the users table
        # Based on our schema: id, username, email, phone_number, password_hash, role, full_name, date_joined, last_login
        user_fields = "id, username, email, phone_number, password_hash, role, full_name, date_joined, last_login"
        if is_email:
            query = f"SELECT {user_fields} FROM users WHERE email = %s"
        else:
            query = f"SELECT {user_fields} FROM users WHERE username = %s"
        
        print(f"[AUTH_DEBUG] Executing query: {query}")
        print(f"[AUTH_DEBUG] With parameter: {username_or_email}")
        
        cursor.execute(query, (username_or_email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            print(f"[AUTH_DEBUG] User '{username_or_email}' not found in database.")
            return None, "Invalid username/email or password."

        # Check if user is verified (we'll assume all users are verified for now since we don't have is_verified column)
        # If you need email verification, you'll need to add the is_verified column back
        user_verified = True  # For now, assume all users are verified
        
        # Bypass email verification for admin users
        if user.get('role') != 'admin' and not user_verified:
            print(f"[AUTH_DEBUG] User '{username_or_email}' found, but email is not verified.")
            return None, "Email not verified. Please check your inbox for an OTP."
        
        if user.get('password_hash') == password_hash:
            print("[AUTH_DEBUG] Password hashes match. Authentication successful.")
            log_activity(user.get('id'), "user_login", f"User logged in: {user.get('username')}")
            update_last_login(user.get('id'))
            return user, "Success"
        else:
            print("[AUTH_DEBUG] Password hashes DO NOT match. Authentication failed.")
            return None, "Invalid username/email or password."
            
    except Exception as e:
        print(f"[AUTH_DEBUG] Exception in authenticate_user: {e}")
        print(f"[AUTH_DEBUG] Exception type: {type(e).__name__}")
        
        # Run diagnostic if it's a database error
        if "mysql" in str(type(e)).lower() or "programming" in str(e).lower():
            print("[AUTH_DEBUG] Running database diagnosis...")
            diagnose_database()
        
        return None, f"Database error: {str(e)}"

def get_all_users():
    """Retrieves all users from the database."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute("SELECT id, username, email, role, full_name, date_joined FROM users ORDER BY id ASC")
        users = cursor.fetchall()
        return users
    except Exception as e:
        st.error(f"Database error fetching users: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_user(user_id, admin_id):
    """
    Deletes a user and all their associated data in a single transaction.
    Handles foreign key constraints by cleaning up dependent records first.
    """
    if user_id == admin_id:
        st.error("Admins cannot delete their own account.")
        return False
        
    conn = get_conn()
    cursor = get_cursor(conn)
    
    try:
        # Start a transaction
        conn.start_transaction()

        # List of tables with a direct user_id foreign key to be deleted
        tables_to_delete_from = ['ratings', 'watchlist', 'history', 'activity_log', 'click_events']
        
        for table in tables_to_delete_from:
            # Check if table exists before trying to delete from it
            cursor.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_id,))

        # For movies, we don't want to delete them. Instead, set uploaded_by to NULL.
        # This requires the column to be nullable.
        cursor.execute("UPDATE movies SET uploaded_by = NULL WHERE uploaded_by = %s", (user_id,))
        
        # Finally, delete the user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        # Commit the transaction
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(admin_id, "admin_delete_user", f"Admin successfully deleted user with ID: {user_id} and all associated data.")
            return True
        else:
            # This case might be hit if the user was already deleted in a separate process
            st.warning("User not found. They may have been deleted already.")
            return False
            
    except Exception as e:
        # If any part of the transaction fails, roll it all back
        conn.rollback()
        st.error(f"Database error during user deletion: {e}")
        # A more specific error for foreign key issues
        if e.errno == 1451:
            st.error("This user cannot be deleted due to remaining dependencies in the database that were not automatically resolved.")
        return False
    finally:
        cursor.close()
        conn.close()

# --- MOVIE MANAGEMENT FUNCTIONS ---

def add_movie(title, item_type, genre, release_year, description, cast, poster_url, trailer_url, audio_languages, uploaded_by):
    """Adds a new movie or series to the database, including audio languages."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            """
            INSERT INTO movies (title, type, genre, release_year, description, cast, poster_url, trailer_url, audio_languages, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (title, item_type, genre, release_year, description, cast, poster_url, trailer_url, audio_languages, uploaded_by)
        )
        conn.commit()
        log_activity(uploaded_by, "add_movie", f"Added movie: {title}")
        return True
    except Exception as err:
        # Error 1062 is for a duplicate entry (e.g., same title)
        if err.errno == 1062:
            st.warning(f"A movie with the title '{title}' already exists.")
        else:
            # For any other database errors
            st.error(f"Database Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_all_movies():
    """Retrieves all movies from the database for the admin panel."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        # Now selecting all fields required by the recommender system
        cursor.execute("SELECT id, title, type, genre, release_year, description, cast, poster_url FROM movies ORDER BY id DESC")
        movies = cursor.fetchall()
        return movies
    except Exception as e:
        st.error(f"Database error fetching movies: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def search_movies(query, genre=None, language=None, year=None, limit=50):
    """
    Searches movies based on a query string and optional filters.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    
    sql = "SELECT * FROM movies WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (title LIKE %s OR description LIKE %s OR cast LIKE %s)"
        search_term = f"%{query}%"
        params.extend([search_term, search_term, search_term])
    
    if genre:
        sql += " AND genre LIKE %s"
        params.append(f"%{genre}%")
    
    if language:
        sql += " AND language = %s"
        params.append(language)
    
    if year:
        sql += " AND release_year = %s"
        params.append(year)
    
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    cursor.execute(sql, params)
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return movies

# --- WATCHLIST & HISTORY FUNCTIONS ---

def add_to_watchlist(user_id, movie_id):
    """Add movie to user's watchlist"""
    conn = get_conn()
    cursor = get_cursor(conn)
    
    try:
        cursor.execute(
            "INSERT IGNORE INTO watchlist (user_id, movie_id) VALUES (%s, %s)",
            (user_id, movie_id)
        )
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(user_id, "add_to_watchlist", f"Added movie {movie_id} to watchlist")
            return True
        return False
    except Exception:
        return False
    finally:
        cursor.close()
        conn.close()

def remove_from_watchlist(user_id, movie_id):
    """Remove movie from user's watchlist"""
    conn = get_conn()
    cursor = get_cursor(conn)
    
    try:
        cursor.execute(
            "DELETE FROM watchlist WHERE user_id = %s AND movie_id = %s",
            (user_id, movie_id)
        )
        conn.commit()
        
        if cursor.rowcount > 0:
            log_activity(user_id, "remove_from_watchlist", f"Removed movie {movie_id} from watchlist")
            return True
        return False
    except Exception:
        return False
    finally:
        cursor.close()
        conn.close()

def get_watchlist(user_id):
    """Get user's watchlist"""
    conn = get_conn()
    cursor = get_cursor(conn)
    
    cursor.execute("""
        SELECT m.* FROM movies m
        JOIN watchlist w ON m.id = w.movie_id
        WHERE w.user_id = %s
        ORDER BY w.added_on DESC
    """, (user_id,))
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return movies

def add_to_history(user_id, movie_id, status='watched'):
    """Add movie to user's history"""
    conn = get_conn()
    cursor = get_cursor(conn)
    
    try:
        cursor.execute("""
            INSERT INTO history (user_id, movie_id, status)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE status = %s, watched_at = CURRENT_TIMESTAMP
        """, (user_id, movie_id, status, status))
        conn.commit()
        
        log_activity(user_id, "add_to_history", f"Added movie {movie_id} to history with status: {status}")
        return True
    except Exception:
        return False
    finally:
        cursor.close()
        conn.close()

def get_history(user_id):
    """Get user's watch history"""
    conn = get_conn()
    cursor = get_cursor(conn)
    
    cursor.execute("""
        SELECT m.*, h.status, h.watched_at FROM movies m
        JOIN history h ON m.id = h.movie_id
        WHERE h.user_id = %s
        ORDER BY h.watched_at DESC
    """, (user_id,))
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return movies

def is_in_watchlist(user_id, movie_id):
    """Checks if a movie is already in the user's watchlist."""
    conn = get_conn()
    if conn is None: return False
    cursor = get_cursor(conn)
    try:
        cursor.execute("SELECT 1 FROM watchlist WHERE user_id = %s AND movie_id = %s", (user_id, movie_id))
        return cursor.fetchone() is not None
    except Exception:
        return False
    finally:
        cursor.close()
        conn.close()

# --- OTP TABLE CREATION ---
def create_otp_table():
    """Create OTP table for email verification and password reset."""
    conn = get_conn()
    cursor = get_cursor(conn)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otps (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            otp_code VARCHAR(10) NOT NULL,
            purpose ENUM('signup', 'reset') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# --- OTP MANAGEMENT FUNCTIONS ---

def generate_otp(length=6):
    """Generate a numeric OTP of given length."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def store_otp(email, otp_code, purpose, expiry_minutes=5):
    """Store OTP in the database with expiry."""
    conn = get_conn()
    cursor = get_cursor(conn)
    expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
    cursor.execute(
        "INSERT INTO otps (email, otp_code, purpose, expires_at) VALUES (%s, %s, %s, %s)",
        (email, otp_code, purpose, expires_at)
    )
    conn.commit()
    cursor.close()
    conn.close()

def validate_otp(email, otp_code, purpose):
    """Validate OTP for email and purpose. Returns True if valid and not expired."""
    conn = get_conn()
    cursor = get_cursor(conn)
    cursor.execute(
        "SELECT * FROM otps WHERE email=%s AND otp_code=%s AND purpose=%s AND expires_at > NOW() ORDER BY created_at DESC LIMIT 1",
        (email, otp_code, purpose)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

def resend_otp(email, purpose='signup'):
    """Deletes old OTPs, generates a new one, stores it, and returns it."""
    # First, delete any existing OTPs for this email and purpose to avoid conflicts
    delete_otps(email, purpose)
    
    # Generate and store a new OTP
    new_otp = generate_otp()
    store_otp(email, new_otp, purpose)
    
    return new_otp

def delete_otps(email, purpose):
    """Delete all OTPs for an email and purpose (cleanup after use)."""
    conn = get_conn()
    cursor = get_cursor(conn)
    cursor.execute(
        "DELETE FROM otps WHERE email=%s AND purpose=%s",
        (email, purpose)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_user_stats(user_id):
    """
    Retrieves various statistics for a given user.
    """
    stats = {
        "member_since": None,
        "total_watched": 0,
        "most_watched_genre": "N/A",
        "average_rating": 0.0,
        "total_reviews": 0
    }
    
    conn = get_conn()
    cursor = get_cursor(conn)
    
    try:
        # Get user's join date
        cursor.execute("SELECT date_joined FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            stats["member_since"] = user_data['date_joined']
            
        # 2. Get total movies watched
        cursor.execute("SELECT COUNT(DISTINCT movie_id) as total FROM history WHERE user_id = %s", (user_id,))
        watched_data = cursor.fetchone()
        if watched_data:
            stats["total_watched"] = watched_data['total']
            
        # 3. Get most watched genre
        cursor.execute("""
            SELECT m.genre, COUNT(h.movie_id) AS watch_count
            FROM history h
            JOIN movies m ON h.movie_id = m.id
            WHERE h.user_id = %s AND m.genre IS NOT NULL AND m.genre != ''
            GROUP BY m.genre
            ORDER BY watch_count DESC
            LIMIT 1
        """, (user_id,))
        genre_data = cursor.fetchone()
        if genre_data:
            stats["most_watched_genre"] = genre_data['genre']
            
        # 4. Get average rating and total reviews
        cursor.execute("SELECT AVG(rating) as avg_r, COUNT(id) as total_r FROM reviews WHERE user_id = %s", (user_id,))
        rating_data = cursor.fetchone()
        if rating_data and rating_data['avg_r'] is not None:
            stats["average_rating"] = float(rating_data['avg_r'])
            stats["total_reviews"] = rating_data['total_r']

    except Exception as err:
        print(f"Error fetching user stats: {err}")
        # Return default stats on error
    
    finally:
        cursor.close()
        conn.close()
        
    return stats

def get_rating_summary(movie_id):
    """
    Calculates the average rating and review count for a given movie.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            """
            SELECT 
                AVG(rating) as average_rating, 
                COUNT(rating) as review_count
            FROM ratings
            WHERE movie_id = %s
            """,
            (movie_id,)
        )
        summary = cursor.fetchone()
        return summary
    except Exception:
        return {'average_rating': 0, 'review_count': 0}
    finally:
        cursor.close()
        conn.close()

def get_reviews_for_movie(movie_id, limit=5):
    """
    Retrieves all reviews for a specific movie, including the username of the reviewer.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            """
            SELECT r.rating, r.review, r.created_at, u.username
            FROM ratings r
            JOIN users u ON r.user_id = u.id
            WHERE r.movie_id = %s
            ORDER BY r.created_at DESC
            LIMIT %s
            """,
            (movie_id, limit)
        )
        reviews = cursor.fetchall()
        return reviews
    except Exception:
        return []
    finally:
        cursor.close()
        conn.close()

def add_or_update_review(movie_id, user_id, rating, review):
    """
    Adds a new review or updates an existing one for a user and movie.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            """
            INSERT INTO ratings (movie_id, user_id, rating, review)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                rating = VALUES(rating),
                review = VALUES(review),
                created_at = CURRENT_TIMESTAMP
            """,
            (movie_id, user_id, rating, review)
        )
        conn.commit()
        return True
    except Exception as err:
        st.error(f"Database error while submitting review: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- You can add more database functions below (e.g., for user auth, movie management) ---

def parse_json_column(data, key_to_extract, limit=3):
    """
    Parses a JSON string from a DataFrame column, extracts specific keys,
    and returns a comma-separated string.
    """
    try:
        items = json.loads(data)
        if isinstance(items, list):
            names = [item.get(key_to_extract, '') for item in items[:limit]]
            return ', '.join(filter(None, names))
    except (json.JSONDecodeError, TypeError):
        return ''
    return ''

def populate_from_tmdb_files(movies_df, credits_df, uploaded_by_id):
    """
    Merges, transforms, and uploads TMDB data from pandas DataFrames.
    """
    st.info("Step 1: Normalizing and merging datasets...")

    # Normalize column names to be safe (lowercase, no extra spaces)
    movies_df.columns = movies_df.columns.str.strip().str.lower()
    credits_df.columns = credits_df.columns.str.strip().str.lower()

    # --- DEBUGGING STEP ---
    st.info("Debugging: Columns found in `movies.csv` after normalization:")
    st.write(list(movies_df.columns))
    # --- END DEBUGGING STEP ---

    # Rename movie_id in credits to 'id' for a clean merge
    if 'movie_id' in credits_df.columns:
        credits_df.rename(columns={'movie_id': 'id'}, inplace=True)
    
    df = movies_df.merge(credits_df, on='id')

    st.info("Step 2: Transforming data for the database...")
    upload_df = pd.DataFrame()
    
    # After merging, pandas appends _x and _y if column names conflict. We'll use title_x.
    upload_df['title'] = df['title_x'].fillna('').str.strip()
    upload_df['type'] = 'Movie'
    upload_df['genre'] = df['genres'].apply(lambda x: parse_json_column(x, 'name', limit=5))
    upload_df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year.fillna(0).astype(int)
    upload_df['description'] = df['overview'].fillna('')
    upload_df['cast'] = df['cast'].apply(lambda x: parse_json_column(x, 'name', limit=4))
    
    # Set poster_url to empty since it's not in the source CSV. We'll fetch it later.
    upload_df['poster_url'] = ''
    
    upload_df['trailer_url'] = ''

    st.info(f"Step 3: Preparing to upload {len(upload_df)} movies...")
    success, message = bulk_upload_movies(upload_df, uploaded_by_id)

    return success, message

def set_user_verified(email):
    """Sets a user's is_verified status to TRUE."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute("UPDATE users SET is_verified = TRUE WHERE email = %s", (email,))
        conn.commit()
        
        # Now log the registration activity
        user = get_user_by_email(email)
        if user:
            log_activity(user['id'], "user_registration", f"New user verified and registered: {user['username']}")
            
        return True
    except Exception as err:
        st.error(f"Database error during verification: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_user_profile(user_id, username, email, phone_number):
    """Updates a user's profile information (username, email, phone number)."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            "UPDATE users SET username = %s, email = %s, phone_number = %s WHERE id = %s",
            (username, email, phone_number, user_id)
        )
        conn.commit()
        # Log the profile update
        log_activity(user_id, "profile_update", f"User {username} updated their profile.")
        return True, "Profile updated successfully!"
    except Exception as err:
        if err.errno == 1062:  # Duplicate entry error code
            return False, "That username or email is already taken. Please choose another."
        else:
            return False, f"A database error occurred: {err}"
    finally:
        cursor.close()
        conn.close()

def change_password(user_id, old_password, new_password):
    """Changes a user's password after verifying the old one."""
    conn = get_conn()
    cursor = get_cursor(conn)
    
    # First, get the current password hash to verify the old password
    try:
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return False, "Could not find user."
            
        # Verify old password
        if user['password_hash'] != hash_password(old_password):
            return False, "Incorrect current password."
            
        # Hash and update to the new password
        new_password_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_password_hash, user_id))
        conn.commit()
        
        log_activity(user_id, "password_change", "User changed their password.")
        return True, "Password updated successfully!"
        
    except Exception as err:
        return False, f"A database error occurred: {err}"
    finally:
        cursor.close()
        conn.close()

# --- WATCH SESSION FUNCTIONS ---

def start_watch_session(user_id, movie_id):
    """Starts a new watch session for a user and movie."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        # Use NOW() to get the current timestamp from the database server
        cursor.execute(
            "INSERT INTO watch_sessions (user_id, movie_id, started_at) VALUES (%s, %s, NOW())",
            (user_id, movie_id)
        )
        conn.commit()
        session_id = cursor.lastrowid
        return session_id
    except Exception as err:
        print(f"Error starting watch session: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def end_watch_session(session_id):
    """Ends a watch session and calculates the duration."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        # Update the row, calculate duration in minutes using TIMESTAMPDIFF
        cursor.execute(
            """
            UPDATE watch_sessions
            SET ended_at = NOW(),
                duration_minutes = TIMESTAMPDIFF(MINUTE, started_at, NOW())
            WHERE id = %s
            """,
            (session_id,)
        )
        conn.commit()
        return True
    except Exception as err:
        print(f"Error ending watch session: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_trending_movies(limit=10):
    """
    Fetches trending movies with a multi-level fallback system.
    1. Tries most-watched movies in the last 30 days.
    2. If none, tries most-watched movies of all time.
    3. If still none, falls back to the highest-rated movies.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        # 1. Try to get movies based on recent watch sessions (last 30 days)
        cursor.execute("""
            SELECT m.*, COUNT(ws.id) as watch_count
            FROM movies m
            JOIN watch_sessions ws ON m.id = ws.movie_id
            WHERE ws.started_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
              AND m.poster_url IS NOT NULL AND m.poster_url LIKE 'http%'
            GROUP BY m.id
            HAVING watch_count > 0
            ORDER BY watch_count DESC
            LIMIT %s
        """, (limit,))
        trending_movies = cursor.fetchall()

        # 2. If no recent trending movies, get top-watched of all time
        if not trending_movies:
            print("No trending movies in last 30 days. Falling back to all-time watch count.")
            cursor.execute("""
                SELECT m.*, COUNT(ws.id) as watch_count
                FROM movies m
                JOIN watch_sessions ws ON m.id = ws.movie_id
                WHERE m.poster_url IS NOT NULL AND m.poster_url LIKE 'http%'
                GROUP BY m.id
                HAVING watch_count > 0
                ORDER BY watch_count DESC
                LIMIT %s
            """, (limit,))
            trending_movies = cursor.fetchall()

        # 3. If still no movies with any watch history, get the highest-rated ones
        if not trending_movies:
            print("No watch history found. Falling back to top-rated movies.")
            cursor.execute("""
                SELECT m.*, AVG(r.rating) as avg_rating, COUNT(r.id) as review_count
                FROM movies m
                JOIN reviews r ON m.id = r.movie_id
                WHERE m.poster_url IS NOT NULL AND m.poster_url LIKE 'http%'
                GROUP BY m.id
                HAVING COUNT(r.id) > 0
                ORDER BY avg_rating DESC, review_count DESC
                LIMIT %s
            """, (limit,))
            trending_movies = cursor.fetchall()

        # 4. If there are no rated movies, fall back to the most recently added movies.
        if not trending_movies:
            print("No rated movies found. Falling back to most recently added movies.")
            cursor.execute("""
                SELECT *
                FROM movies
                WHERE poster_url IS NOT NULL AND poster_url LIKE 'http%'
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            trending_movies = cursor.fetchall()
            
        return trending_movies
    except Exception as err:
        print(f"Error getting trending movies: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def update_movie_poster(movie_id, new_poster_url):
    """Updates the poster URL for a specific movie."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        print(f"Attempting to update poster for movie_id: {movie_id}")
        cursor.execute(
            "UPDATE movies SET poster_url = %s WHERE id = %s",
            (new_poster_url, movie_id)
        )
        conn.commit()
        print(f"Update executed. Rows affected: {cursor.rowcount}")
        return cursor.rowcount > 0
    except Exception as e:
        st.error(f"Database error updating poster: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def add_recommendation_feedback(user_id, movie_id, feedback='not_interested'):
    """Adds feedback for a recommended movie."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            "INSERT INTO user_recommendation_feedback (user_id, movie_id, feedback) VALUES (%s, %s, %s)",
            (user_id, movie_id, feedback)
        )
        conn.commit()
        return True
    except Exception as err:
        if err.errno == 1062: # Duplicate entry
            return True # Already recorded, treat as success
        print(f"Database error providing feedback: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_recommendation_feedback_ids(user_id):
    """Gets all movie IDs a user has marked as not interested."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            "SELECT movie_id FROM user_recommendation_feedback WHERE user_id = %s AND feedback = 'not_interested'",
            (user_id,)
        )
        excluded_ids = [row['movie_id'] for row in cursor.fetchall()]
        return excluded_ids
    except Exception as err:
        print(f"Database error fetching feedback: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_reviews_for_user(user_id):
    """
    Retrieves all reviews written by a specific user, including movie details.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            '''
            SELECT r.id, r.rating, r.review, r.created_at, m.title, m.release_year, m.genre
            FROM reviews r
            JOIN movies m ON r.movie_id = m.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
            ''',
            (user_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching user reviews: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_user_badges(user_id):
    """
    Returns a list of badges/achievements for the user based on their activity.
    """
    badges = []
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        # First Watch
        cursor.execute("SELECT COUNT(*) as cnt FROM history WHERE user_id = %s", (user_id,))
        watched_count = cursor.fetchone()['cnt']
        if watched_count >= 1:
            badges.append({'name': 'First Watch', 'description': 'Watched your first movie/series!'})
        # 10 Movies Watched
        if watched_count >= 10:
            badges.append({'name': '10 Movies Watched', 'description': 'Watched 10 or more movies/series!'})
        # First Review
        cursor.execute("SELECT COUNT(*) as cnt FROM reviews WHERE user_id = %s", (user_id,))
        review_count = cursor.fetchone()['cnt']
        if review_count >= 1:
            badges.append({'name': 'First Review', 'description': 'Wrote your first review!'})
        # Genre Master (watched 5+ in a genre)
        cursor.execute('''
            SELECT m.genre, COUNT(*) as cnt
            FROM history h
            JOIN movies m ON h.movie_id = m.id
            WHERE h.user_id = %s AND m.genre IS NOT NULL AND m.genre != ''
            GROUP BY m.genre
        ''', (user_id,))
        for row in cursor.fetchall():
            if row['cnt'] >= 5:
                badges.append({'name': f"{row['genre']} Master", 'description': f"Watched 5+ in {row['genre']} genre!"})
    except Exception as e:
        print(f"Error fetching badges: {e}")
    finally:
        cursor.close()
        conn.close()
    return badges 

def update_user_profile_custom(user_id, profile_pic, bio, favorite_genres):
    """
    Updates the user's profile picture, bio, and favorite genres.
    favorite_genres is a comma-separated string.
    Assumes 'bio' and 'favorite_genres' columns exist in the users table.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            """
            UPDATE users
            SET profile_pic = %s, bio = %s, favorite_genres = %s
            WHERE id = %s
            """,
            (profile_pic, bio, favorite_genres, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_continue_watching(user_id):
    """
    Returns a list of movies/series the user started but has not finished.
    Includes active watch sessions (no ended_at) or history status not 'watched'.
    """
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        # Active sessions (not ended)
        cursor.execute('''
            SELECT m.*
            FROM watch_sessions ws
            JOIN movies m ON ws.movie_id = m.id
            WHERE ws.user_id = %s AND ws.ended_at IS NULL
        ''', (user_id,))
        active = cursor.fetchall() or []
        # History entries not marked as 'watched'
        cursor.execute('''
            SELECT m.*
            FROM history h
            JOIN movies m ON h.movie_id = m.id
            WHERE h.user_id = %s AND (h.status IS NULL OR h.status != 'watched')
        ''', (user_id,))
        partial = cursor.fetchall() or []
        # Combine and deduplicate by movie id
        seen = set()
        result = []
        for m in active + partial:
            if m['id'] not in seen:
                result.append(m)
                seen.add(m['id'])
        return result
    except Exception as e:
        print(f"Error fetching continue watching: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_watchlist_count(movie_id):
    """Return the number of users who have added the movie to their watchlist."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute("SELECT COUNT(*) FROM watchlist WHERE movie_id = %s", (movie_id,))
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"[DB] get_watchlist_count error: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def get_review_count(movie_id):
    """Return the number of reviews for the movie."""
    conn = get_conn()
    cursor = get_cursor(conn)
    try:
        cursor.execute("SELECT COUNT(*) FROM ratings WHERE movie_id = %s AND review IS NOT NULL AND review != ''", (movie_id,))
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        print(f"[DB] get_review_count error: {e}")
        return 0
    finally:
        cursor.close()
        conn.close() 