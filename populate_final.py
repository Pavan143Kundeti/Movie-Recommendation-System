import pandas as pd
import mysql.connector
import ast
import sys

def populate_database():
    """Final database population script"""
    print("=== Starting Database Population ===")
    
    # Step 1: Test MySQL connection (same as Streamlit app)
    print("\n1. Testing MySQL connection...")
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root", 
            password="Pavan@3048",
            database="movie_db"
        )
        print("✅ MySQL connection successful!")
    except mysql.connector.Error as err:
        print(f"❌ MySQL connection failed: {err}")
        return
    
    # Step 2: Read CSV files
    print("\n2. Reading CSV files...")
    try:
        print("Reading movies CSV...")
        movies_df = pd.read_csv('tmdb_5000_movies.csv')
        print(f"✅ Movies CSV loaded: {len(movies_df)} rows")
        
        print("Reading credits CSV...")
        credits_df = pd.read_csv('tmdb_5000_credits.csv')
        print(f"✅ Credits CSV loaded: {len(credits_df)} rows")
    except Exception as e:
        print(f"❌ Error reading CSV files: {e}")
        connection.close()
        return
    
    # Step 3: Process data
    print("\n3. Processing data...")
    try:
        # Take only first 10 movies for testing
        movies_df = movies_df.head(10)
        credits_df = credits_df.head(10)
        
        # Merge data
        merged_df = movies_df.merge(credits_df, left_on='id', right_on='movie_id', how='left')
        print(f"✅ Merged data: {len(merged_df)} movies")
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        connection.close()
        return
    
    # Step 4: Insert into database
    print("\n4. Inserting into database...")
    cursor = connection.cursor()
    
    insert_query = """
    INSERT INTO movies (title, type, genre, release_year, description, cast, poster_url, trailer_url, uploaded_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    success_count = 0
    
    for index, row in merged_df.iterrows():
        try:
            # Extract basic data
            title = str(row['title'])[:255] if pd.notna(row['title']) else "Unknown Title"
            print(f"Processing: {title}")
            
            # Extract genres
            try:
                if pd.notna(row['genres']):
                    genres_list = ast.literal_eval(str(row['genres']))
                    genre_names = [genre['name'] for genre in genres_list]
                    genre = ', '.join(genre_names[:3])  # Take first 3 genres
                else:
                    genre = "Unknown"
            except:
                genre = "Unknown"
            
            # Extract release year
            try:
                if pd.notna(row['release_date']):
                    date_str = str(row['release_date'])
                    year = int(date_str.split('-')[0]) if '-' in date_str else 2000
                else:
                    year = 2000
            except:
                year = 2000
            
            # Extract description
            description = str(row['overview'])[:500] if pd.notna(row['overview']) else "No description available"
            
            # Extract cast
            try:
                if pd.notna(row['cast']):
                    cast_list = ast.literal_eval(str(row['cast']))
                    cast_names = [person['name'] for person in cast_list[:3]]  # Take first 3 cast members
                    cast = ', '.join(cast_names)
                else:
                    cast = "Unknown"
            except:
                cast = "Unknown"
            
            # Insert into database
            cursor.execute(insert_query, (
                title, "Movie", genre, year, description, 
                cast, "", "", 1  # Empty poster/trailer URLs, uploaded_by = 1
            ))
            
            success_count += 1
            print(f"✅ Inserted: {title}")
            
        except Exception as e:
            print(f"❌ Error inserting {row.get('title', 'Unknown')}: {e}")
            continue
    
    # Commit and close
    connection.commit()
    cursor.close()
    connection.close()
    
    print(f"\n=== COMPLETED ===")
    print(f"Successfully inserted {success_count} movies into the database!")

if __name__ == "__main__":
    populate_database() 