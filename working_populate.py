import pandas as pd
import mysql.connector
import ast

def db_connect():
    """Same connection function as in your Streamlit app"""
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

def populate_database():
    """Populate database with movie data"""
    print("=== Starting Database Population ===")
    
    # Connect to database
    print("1. Connecting to database...")
    conn = db_connect()
    if conn is None:
        print("Failed to connect to database!")
        return
    
    print("✅ Connected to database!")
    
    # Read CSV files
    print("\n2. Reading CSV files...")
    try:
        movies_df = pd.read_csv('tmdb_5000_movies.csv')
        print(f"✅ Movies CSV: {len(movies_df)} rows")
        
        credits_df = pd.read_csv('tmdb_5000_credits.csv')
        print(f"✅ Credits CSV: {len(credits_df)} rows")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        conn.close()
        return
    
    # Process data
    print("\n3. Processing data...")
    try:
        # Take first 5 movies for testing
        movies_df = movies_df.head(5)
        credits_df = credits_df.head(5)
        
        # Merge data
        merged_df = movies_df.merge(credits_df, left_on='id', right_on='movie_id', how='left')
        print(f"✅ Merged data: {len(merged_df)} movies")
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        conn.close()
        return
    
    # Insert data
    print("\n4. Inserting movies...")
    cursor = conn.cursor()
    
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
            try:
                if pd.notna(row['genres']):
                    genres_list = ast.literal_eval(str(row['genres']))
                    genre_names = [genre['name'] for genre in genres_list]
                    genre = ', '.join(genre_names[:3])
                else:
                    genre = "Unknown"
            except:
                genre = "Unknown"
            
            # Extract year
            try:
                if pd.notna(row['release_date']):
                    date_str = str(row['release_date'])
                    year = int(date_str.split('-')[0]) if '-' in date_str else 2000
                else:
                    year = 2000
            except:
                year = 2000
            
            # Extract description
            description = str(row['overview'])[:500] if pd.notna(row['overview']) else "No description"
            
            # Extract cast
            try:
                if pd.notna(row['cast']):
                    cast_list = ast.literal_eval(str(row['cast']))
                    cast_names = [person['name'] for person in cast_list[:3]]
                    cast = ', '.join(cast_names)
                else:
                    cast = "Unknown"
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
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n=== COMPLETED ===")
    print(f"Successfully inserted {success_count} movies!")

if __name__ == "__main__":
    populate_database() 