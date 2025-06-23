import pandas as pd
import mysql.connector
import ast

def populate_database():
    """Simple database population script"""
    print("=== Simple Database Population ===")
    
    # Direct connection (bypassing Streamlit secrets)
    print("Connecting to MySQL...")
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pavan@3048",
        database="movie_db"
    )
    print("✅ Connected to MySQL!")
    
    # Read CSV files
    print("Reading CSV files...")
    movies_df = pd.read_csv('tmdb_5000_movies.csv')
    credits_df = pd.read_csv('tmdb_5000_credits.csv')
    print(f"✅ Read {len(movies_df)} movies and {len(credits_df)} credits")
    
    # Take first 20 movies
    movies_df = movies_df.head(20)
    credits_df = credits_df.head(20)
    
    # Merge data
    merged_df = movies_df.merge(credits_df, left_on='id', right_on='movie_id', how='left')
    print(f"✅ Merged {len(merged_df)} movies")
    
    # Insert data
    cursor = connection.cursor()
    insert_query = """
    INSERT INTO movies (title, type, genre, release_year, description, cast, poster_url, trailer_url, uploaded_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    success_count = 0
    
    for index, row in merged_df.iterrows():
        try:
            # Extract data
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
            
            # Insert
            cursor.execute(insert_query, (
                title, "Movie", genre, year, description, 
                cast, "", "", 1
            ))
            
            success_count += 1
            print(f"✅ Inserted: {title}")
            
        except Exception as e:
            print(f"❌ Error with {row.get('title', 'Unknown')}: {e}")
            continue
    
    # Commit and close
    connection.commit()
    cursor.close()
    connection.close()
    
    print(f"\n=== COMPLETED ===")
    print(f"Successfully inserted {success_count} movies!")

if __name__ == "__main__":
    populate_database() 