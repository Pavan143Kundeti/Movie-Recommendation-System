import pandas as pd

# Try to import scikit-learn components with fallback
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Using simple recommendation fallback.")

# This global variable will cache the computed similarity matrix
similarity_matrix_cache = None
movie_data_cache = None

def build_recommendation_model(movies_df):
    """
    Builds and returns the cosine similarity matrix for the movies.
    """
    global similarity_matrix_cache, movie_data_cache
    
    if not SKLEARN_AVAILABLE:
        # Fallback: just cache the movie data for simple recommendations
        movie_data_cache = movies_df
        similarity_matrix_cache = None
        return None, movies_df
    
    # --- Feature Engineering ---
    # Create a 'soup' of text features for each movie
    movies_df['soup'] = movies_df['genre'].fillna('') + ' ' + \
                        movies_df['description'].fillna('') + ' ' + \
                        movies_df['cast'].fillna('')
    
    # --- Vectorization ---
    # Use TF-IDF to convert the text soup into a matrix of numerical features
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['soup'])
    
    # --- Similarity Calculation ---
    # Compute the cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # Cache the results
    similarity_matrix_cache = cosine_sim
    movie_data_cache = movies_df
    
    return cosine_sim, movies_df

def get_recommendations(movie_title, num_recommendations=10):
    """
    Gets movie recommendations based on a given movie title.
    """
    if movie_data_cache is None:
        # This should ideally be handled by pre-loading the model
        return pd.DataFrame() # Return empty if model not built

    if not SKLEARN_AVAILABLE or similarity_matrix_cache is None:
        # Fallback: return movies with similar genres
        return get_simple_recommendations(movie_title, num_recommendations)

    # Create a mapping of movie titles to indices
    indices = pd.Series(movie_data_cache.index, index=movie_data_cache['title']).drop_duplicates()

    try:
        # Get the index of the movie that matches the title
        idx = indices[movie_title]
    except KeyError:
        return pd.DataFrame() # Movie not found

    # Get the pairwise similarity scores of all movies with that movie
    sim_scores = list(enumerate(similarity_matrix_cache[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:num_recommendations+1]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Get the recommended movies from the cache
    recommended_movies = movie_data_cache.iloc[movie_indices]
    
    # --- Remove Duplicates ---
    # Drop movies with the same title, keeping the first occurrence
    recommended_movies = recommended_movies.drop_duplicates(subset='title', keep='first')

    # --- Filter for Posters ---
    # Only recommend movies that have a valid-looking poster URL.
    if 'poster_url' in recommended_movies.columns:
        recommended_movies = recommended_movies[
            recommended_movies['poster_url'].notna() & 
            recommended_movies['poster_url'].str.strip().str.startswith('http', na=False)
        ]

    # Return the top N unique recommendations
    return recommended_movies.head(num_recommendations)

def get_simple_recommendations(movie_title, num_recommendations=10):
    """
    Simple fallback recommendation system based on genre similarity.
    """
    if movie_data_cache is None:
        return pd.DataFrame()
    
    try:
        # Find the target movie
        target_movie = movie_data_cache[movie_data_cache['title'] == movie_title].iloc[0]
        target_genre = target_movie.get('genre', '')
        
        if not target_genre:
            # If no genre, return random movies
            return movie_data_cache.sample(min(num_recommendations, len(movie_data_cache)))
        
        # Find movies with similar genres
        similar_movies = movie_data_cache[
            (movie_data_cache['genre'].str.contains(target_genre, case=False, na=False)) &
            (movie_data_cache['title'] != movie_title)
        ]
        
        if len(similar_movies) < num_recommendations:
            # If not enough similar movies, add some random ones
            remaining = num_recommendations - len(similar_movies)
            other_movies = movie_data_cache[
                (~movie_data_cache['genre'].str.contains(target_genre, case=False, na=False)) &
                (movie_data_cache['title'] != movie_title)
            ]
            if len(other_movies) > 0:
                additional = other_movies.sample(min(remaining, len(other_movies)))
                similar_movies = pd.concat([similar_movies, additional])
        
        # Filter for posters and return
        if 'poster_url' in similar_movies.columns:
            similar_movies = similar_movies[
                similar_movies['poster_url'].notna() & 
                similar_movies['poster_url'].str.strip().str.startswith('http', na=False)
            ]
        
        return similar_movies.head(num_recommendations)
        
    except (IndexError, KeyError):
        # If anything goes wrong, return random movies
        return movie_data_cache.sample(min(num_recommendations, len(movie_data_cache))) 