import pandas as pd
import ast
import sys
import os

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import the database module from your working app
from database import db_connect

def populate_database():
    """Populate database using the working database module"""
    print("=== Populating Database with CSV Data ===")
    
    # Connect using the working database module
    print("1. Connecting to database...")
    connection = db_connect()
    if connection is None:
        print("❌ Failed to connect to database!")
        return
    
    print("✅ Connected!")
    
    try:
        # Read CSV files
        print("\n2. Reading CSV files...")
        movies_df = pd.read_csv('tmdb_5000_movies.csv')
        print(f"✅ Movies CSV: {len(movies_df)} rows")
        
        credits_df = pd.read_csv('tmdb_5000_credits.csv')
        print(f"✅ Credits CSV: {len(credits_df)} rows")
        
        # Process data
        print("\n3. Processing data...")
        # Take first 100 movies
        movies_df = movies_df.head(100)
        credits_df = credits_df.head(100)
        
        # Merge data
        merged_df = movies_df.merge(credits_df, left_on='id', right_on='movie_id', how='left')
        print(f"✅ Merged data: {len(merged_df)} movies")
        
        # Insert data
        print("\n4. Inserting movies...")
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO movies (title, type, genre, release_year, description, cast, poster_url, trailer_url, uploaded_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        
        for index, row in merged_df.iterrows():
            try:
                # Extract title
                title = str(row['title'])[:255] if pd.notna(row['title']) else "Unknown"
                
                # Extract genres
                genre = "Unknown"
                if pd.notna(row['genres']):
                    try:
                        genres_list = ast.literal_eval(str(row['genres']))
                        genre_names = [genre['name'] for genre in genres_list]
                        genre = ', '.join(genre_names[:3])
                    except:
                        genre = "Unknown"
                
                # Extract year
                year = 2000
                if pd.notna(row['release_date']):
                    try:
                        date_str = str(row['release_date'])
                        if '-' in date_str:
                            year = int(date_str.split('-')[0])
                    except:
                        year = 2000
                
                # Extract description
                description = "No description available"
                if pd.notna(row['overview']):
                    description = str(row['overview'])[:500]
                
                # Extract cast
                cast = "Unknown"
                if pd.notna(row['cast']):
                    try:
                        cast_list = ast.literal_eval(str(row['cast']))
                        cast_names = [person['name'] for person in cast_list[:3]]
                        cast = ', '.join(cast_names)
                    except:
                        cast = "Unknown"
                
                # Insert into database
                cursor.execute(insert_query, (
                    title, "Movie", genre, year, description, 
                    cast, "", "", 1
                ))
                
                success_count += 1
                if success_count % 20 == 0:
                    print(f"✅ Inserted {success_count} movies...")
                
            except Exception as e:
                print(f"❌ Error with {row.get('title', 'Unknown')}: {e}")
                continue
        
        # Commit and close
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"\n=== COMPLETED ===")
        print(f"Successfully inserted {success_count} movies from CSV!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if connection:
            connection.close()

if __name__ == "__main__":
    populate_database() 