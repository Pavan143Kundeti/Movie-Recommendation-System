import streamlit as st
import requests

BASE_URL = "https://api.themoviedb.org/3"
BASE_POSTER_URL = "https://image.tmdb.org/t/p/w500"

def get_api_key():
    """Retrieves the TMDb API key from Streamlit secrets."""
    try:
        return st.secrets["tmdb"]["api_key"]
    except (KeyError, FileNotFoundError):
        st.error("TMDb API key not found. Please add it to your secrets.toml file.")
        return None

def find_poster_url(title, year=None):
    """
    Finds a movie's poster URL on TMDb by its title and release year.
    Returns the full poster URL if found, otherwise None.
    """
    api_key = get_api_key()
    if not api_key:
        return None

    # --- Search for the movie ---
    search_url = f"{BASE_URL}/search/movie"
    params = {"api_key": api_key, "query": title}
    if year:
        params["year"] = year
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status() # Raises an HTTPError for bad responses
        data = response.json()
        
        # --- Find the best match ---
        if data.get("results"):
            # The first result is often the best match, especially with a year filter.
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"{BASE_POSTER_URL}{poster_path}"
        
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error calling TMDb API: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing TMDb response for '{title}': {e}")
        return None 