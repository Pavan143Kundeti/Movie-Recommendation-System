import pandas as pd
import mysql.connector
import json
import ast
from datetime import datetime
import re

def connect_to_mysql():
    """Connect to MySQL database"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pavan@3048",
            database="movie_db"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def extract_genres(genres_str):
    """Extract genre names from JSON string"""
    try:
        if pd.isna(genres_str) or genres_str == '':
            return "Unknown"
        
        # Parse the JSON string
        genres_list = ast.literal_eval(genres_str)
        genre_names = [genre['name'] for genre in genres_list]
        return ', '.join(genre_names)
    except:
        return "Unknown"

def extract_cast(cast_str):
    """Extract cast names from JSON string"""
    try:
        if pd.isna(cast_str) or cast_str == '':
            return "Unknown"
        
        # Parse the JSON string
        cast_list = ast.literal_eval(cast_str)
        # Get top 5 cast members
        cast_names = [person['name'] for person in cast_list[:5]]
        return ', '.join(cast_names)
    except:
        return "Unknown"

def extract_release_year(release_date):
    """Extract year from release date"""
    try:
        if pd.isna(release_date) or release_date == '':
            return 2000
        
        # Parse date and extract year
        date_obj = pd.to_datetime(release_date)
        return date_obj.year
    except:
        return 2000

def clean_text(text):
    """Clean and truncate text fields"""
    if pd.isna(text) or text == '':
        return "No description available"
    
    # Remove special characters and truncate
    cleaned = re.sub(r'[^\w\s.,!?-]', '', str(text))
    return cleaned[:500] if len(cleaned) > 500 else cleaned

def create_poster_url(movie_id):
    """Create poster URL using TMDB API format"""
    return f"https://image.tmdb.org/t/p/w500/placeholder_{movie_id}.jpg"

def populate_database():
    """Main function to populate the database"""
    print("Starting database population...")
    
    # Connect to MySQL
    connection = connect_to_mysql()
    if not connection:
        print("Failed to connect to MySQL. Please check your credentials.")
        return
    
    cursor = connection.cursor()
    
    try:
        # Read the CSV files
        print("Reading movies CSV file...")
        movies_df = pd.read_csv('tmdb_5000_movies.csv')
        
        print("Reading credits CSV file...")
        credits_df = pd.read_csv('tmdb_5000_credits.csv')
        
        # Merge the dataframes on movie_id
        print("Merging data...")
        merged_df = movies_df.merge(credits_df, left_on='id', right_on='movie_id', how='left')
        
        # Limit to first 100 movies for testing (you can remove this limit)
        merged_df = merged_df.head(100)
        
        print(f"Processing {len(merged_df)} movies...")
        
        # Prepare the insert statement
        insert_query = """
        INSERT INTO movies (title, type, genre, release_year, description, cast, poster_url, trailer_url, uploaded_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Process each movie
        for index, row in merged_df.iterrows():
            try:
                # Extract and process data
                title = clean_text(row['title'])
                genre = extract_genres(row['genres'])
                release_year = extract_release_year(row['release_date'])
                description = clean_text(row['overview'])
                cast = extract_cast(row['cast'])
                poster_url = create_poster_url(row['id'])
                
                # Set default values
                movie_type = "Movie"  # Default to Movie
                trailer_url = ""  # No trailer URL in the data
                uploaded_by = 1  # Default admin user ID
                
                # Insert into database
                cursor.execute(insert_query, (
                    title, movie_type, genre, release_year, description, 
                    cast, poster_url, trailer_url, uploaded_by
                ))
                
                if (index + 1) % 10 == 0:
                    print(f"Processed {index + 1} movies...")
                    
            except Exception as e:
                print(f"Error processing movie {row.get('title', 'Unknown')}: {e}")
                continue
        
        # Commit the changes
        connection.commit()
        print(f"Successfully inserted {len(merged_df)} movies into the database!")
        
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    # First, ensure the database exists
    print("Creating database if it doesn't exist...")
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pavan@3048"
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS movie_db")
        connection.commit()
        cursor.close()
        connection.close()
        print("Database 'movie_db' is ready!")
    except Exception as e:
        print(f"Error creating database: {e}")
        exit(1)
    
    # Populate the database
    populate_database() 