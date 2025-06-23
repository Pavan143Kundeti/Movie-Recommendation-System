import streamlit as st
import pandas as pd

def display_movie_poster(poster_url, title):
    """Helper function to display movie poster with error handling"""
    default_poster = "https://via.placeholder.com/300x450/2E2E2E/FFFFFF?text=🎬+No+Poster"
    
    if poster_url and poster_url.strip():
        try:
            st.image(poster_url, caption=title)
        except Exception as e:
            st.image(default_poster, caption=title)
    else:
        st.image(default_poster, caption=title)

def test_movie_display():
    st.title("🎬 Movie Poster Display Test")
    
    # Sample movie data
    sample_movies = [
        {
            'title': 'The Shawshank Redemption',
            'genre': 'Drama',
            'release_year': 1994,
            'description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
            'cast': 'Tim Robbins, Morgan Freeman',
            'poster_url': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg'
        },
        {
            'title': 'The Godfather',
            'genre': 'Crime, Drama',
            'release_year': 1972,
            'description': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
            'cast': 'Marlon Brando, Al Pacino',
            'poster_url': 'https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg'
        },
        {
            'title': 'Pulp Fiction',
            'genre': 'Crime, Drama',
            'release_year': 1994,
            'description': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.',
            'cast': 'John Travolta, Uma Thurman',
            'poster_url': 'https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg'
        },
        {
            'title': 'Movie with No Poster',
            'genre': 'Comedy',
            'release_year': 2023,
            'description': 'This movie has no poster URL to test the default image functionality.',
            'cast': 'Unknown Actor',
            'poster_url': ''
        },
        {
            'title': 'Movie with Broken URL',
            'genre': 'Action',
            'release_year': 2023,
            'description': 'This movie has a broken poster URL to test error handling.',
            'cast': 'Test Actor',
            'poster_url': 'https://broken-url-that-does-not-exist.com/poster.jpg'
        }
    ]
    
    st.header("📺 Sample Movies Display")
    st.write("Testing movie poster display with various scenarios:")
    
    # Display movies in a responsive grid (3 movies per row)
    num_columns = 3
    cols = st.columns(num_columns)
    
    for i, movie in enumerate(sample_movies):
        col = cols[i % num_columns]
        
        with col:
            # Create a card-like container for each movie
            with st.container():
                # Movie poster
                display_movie_poster(movie['poster_url'], movie['title'])
                
                # Movie title
                st.markdown(f"**{movie['title']}**")
                
                # Movie details
                st.caption(f"🎬 Movie | 🎭 {movie['genre']} | 📅 {movie['release_year']}")
                
                # Movie description (truncated if too long)
                description = movie['description']
                if len(description) > 120:
                    description = description[:120] + "..."
                st.write(description)
                
                # Cast information
                st.caption(f"👥 Cast: {movie['cast']}")
                
                # Add some spacing between movie cards
                st.markdown("---")
    
    st.success("✅ Movie poster display test completed!")
    st.info("This test shows how the app handles: valid poster URLs, empty URLs, and broken URLs.")

if __name__ == "__main__":
    test_movie_display() 