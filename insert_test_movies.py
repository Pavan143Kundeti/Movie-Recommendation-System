import mysql.connector

def insert_test_movies():
    """Insert a few test movies manually"""
    print("=== Inserting Test Movies ===")
    
    try:
        # Connect to database
        print("Connecting to database...")
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pavan@3048",
            database="movie_db"
        )
        print("✅ Connected!")
        
        cursor = connection.cursor()
        
        # Test movies data
        test_movies = [
            ("The Shawshank Redemption", "Movie", "Drama", 1994, 
             "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.", 
             "Tim Robbins, Morgan Freeman", "", "", 1),
            
            ("The Godfather", "Movie", "Crime, Drama", 1972,
             "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
             "Marlon Brando, Al Pacino", "", "", 1),
            
            ("Pulp Fiction", "Movie", "Crime, Drama", 1994,
             "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
             "John Travolta, Uma Thurman", "", "", 1),
            
            ("The Dark Knight", "Movie", "Action, Crime, Drama", 2008,
             "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
             "Christian Bale, Heath Ledger", "", "", 1),
            
            ("Fight Club", "Movie", "Drama", 1999,
             "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.",
             "Brad Pitt, Edward Norton", "", "", 1)
        ]
        
        # Insert query
        insert_query = """
        INSERT INTO movies (title, type, genre, release_year, description, cast, poster_url, trailer_url, uploaded_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Insert each movie
        for movie in test_movies:
            cursor.execute(insert_query, movie)
            print(f"✅ Inserted: {movie[0]}")
        
        # Commit changes
        connection.commit()
        print(f"\n✅ Successfully inserted {len(test_movies)} test movies!")
        
        # Close connection
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
    except Exception as e:
        print(f"❌ General error: {e}")

if __name__ == "__main__":
    insert_test_movies() 