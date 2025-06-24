#!/usr/bin/env python3
"""
Script to add sample movie data to the database
"""

import mysql.connector
import streamlit as st

# Database configuration
DB_CONFIG = {
    'host': 'sql12.freesqldatabase.com',
    'user': 'sql12786417',
    'password': 'm46Km6gKDb',
    'database': 'sql12786417'
}

def get_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def add_sample_movies():
    """Add sample movies to the database"""
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Sample movies data
    sample_movies = [
        {
            'title': 'The Shawshank Redemption',
            'type': 'Movie',
            'genre': 'Drama',
            'description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
            'release_year': 1994,
            'cast': 'Tim Robbins, Morgan Freeman, Bob Gunton',
            'poster_url': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=6hB3S9bIaco',
            'audio_languages': 'English',
            'uploaded_by': 1
        },
        {
            'title': 'The Godfather',
            'type': 'Movie',
            'genre': 'Crime, Drama',
            'description': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
            'release_year': 1972,
            'cast': 'Marlon Brando, Al Pacino, James Caan',
            'poster_url': 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=sY1S34973zA',
            'audio_languages': 'English, Italian',
            'uploaded_by': 1
        },
        {
            'title': 'The Dark Knight',
            'type': 'Movie',
            'genre': 'Action, Crime, Drama',
            'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
            'release_year': 2008,
            'cast': 'Christian Bale, Heath Ledger, Aaron Eckhart',
            'poster_url': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=EXeTwQWrcwY',
            'audio_languages': 'English',
            'uploaded_by': 1
        },
        {
            'title': 'Pulp Fiction',
            'type': 'Movie',
            'genre': 'Crime, Drama',
            'description': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.',
            'release_year': 1994,
            'cast': 'John Travolta, Uma Thurman, Samuel L. Jackson',
            'poster_url': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=s7EdQ4FqbhY',
            'audio_languages': 'English',
            'uploaded_by': 1
        },
        {
            'title': 'Fight Club',
            'type': 'Movie',
            'genre': 'Drama',
            'description': 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.',
            'release_year': 1999,
            'cast': 'Brad Pitt, Edward Norton, Helena Bonham Carter',
            'poster_url': 'https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=SUXWAEX2jlg',
            'audio_languages': 'English',
            'uploaded_by': 1
        },
        {
            'title': 'Inception',
            'type': 'Movie',
            'genre': 'Action, Adventure, Sci-Fi',
            'description': 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
            'release_year': 2010,
            'cast': 'Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page',
            'poster_url': 'https://image.tmdb.org/t/p/w500/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=YoHD9XEInc0',
            'audio_languages': 'English',
            'uploaded_by': 1
        },
        {
            'title': 'The Matrix',
            'type': 'Movie',
            'genre': 'Action, Sci-Fi',
            'description': 'A computer programmer discovers that reality as he knows it is a simulation created by machines, and joins a rebellion to break free.',
            'release_year': 1999,
            'cast': 'Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss',
            'poster_url': 'https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=m8e-FF8MsqU',
            'audio_languages': 'English',
            'uploaded_by': 1
        },
        {
            'title': 'Goodfellas',
            'type': 'Movie',
            'genre': 'Biography, Crime, Drama',
            'description': 'The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito.',
            'release_year': 1990,
            'cast': 'Robert De Niro, Ray Liotta, Joe Pesci',
            'poster_url': 'https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=qo5jJpHtI1Y',
            'audio_languages': 'English',
            'uploaded_by': 1
        },
        {
            'title': 'The Silence of the Lambs',
            'type': 'Movie',
            'genre': 'Crime, Drama, Thriller',
            'description': 'A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer, a madman who skins his victims.',
            'release_year': 1991,
            'cast': 'Jodie Foster, Anthony Hopkins, Lawrence A. Bonney',
            'poster_url': 'https://image.tmdb.org/t/p/w500/rplLJ2hPcOQmkFhTqUte0MkEaO2.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=W6Mm8Sbe__o',
            'audio_languages': 'English',
            'uploaded_by': 1
        },
        {
            'title': 'Interstellar',
            'type': 'Movie',
            'genre': 'Adventure, Drama, Sci-Fi',
            'description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'release_year': 2014,
            'cast': 'Matthew McConaughey, Anne Hathaway, Jessica Chastain',
            'poster_url': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
            'trailer_url': 'https://www.youtube.com/watch?v=2LqzF5WauAw',
            'audio_languages': 'English',
            'uploaded_by': 1
        }
    ]
    
    try:
        # Check if movies already exist
        cursor.execute("SELECT COUNT(*) FROM movies")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Database already has {count} movies. Skipping sample data insertion.")
            return True
        
        # Insert sample movies
        for movie in sample_movies:
            sql = """
                INSERT INTO movies (title, type, genre, description, release_year, cast, poster_url, trailer_url, audio_languages, uploaded_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                movie['title'],
                movie['type'],
                movie['genre'],
                movie['description'],
                movie['release_year'],
                movie['cast'],
                movie['poster_url'],
                movie['trailer_url'],
                movie['audio_languages'],
                movie['uploaded_by']
            )
            
            cursor.execute(sql, values)
            print(f"✓ Added movie: {movie['title']}")
        
        conn.commit()
        print(f"\n✓ Successfully added {len(sample_movies)} sample movies!")
        return True
        
    except Exception as e:
        print(f"Error adding sample movies: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def main():
    print("=== Adding Sample Movies ===")
    
    success = add_sample_movies()
    
    if success:
        print("\n✓ Sample movies added successfully!")
        print("You can now run the Streamlit app and see the movies.")
    else:
        print("\n✗ Failed to add sample movies.")

if __name__ == "__main__":
    main() 