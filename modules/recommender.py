import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# This global variable will cache the computed similarity matrix
similarity_matrix_cache = None
movie_data_cache = None

def build_recommendation_model(movies_df):
    """
    Builds and returns the cosine similarity matrix for the movies.
    """
    global similarity_matrix_cache, movie_data_cache
    
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
    if similarity_matrix_cache is None or movie_data_cache is None:
        # This should ideally be handled by pre-loading the model
        return pd.DataFrame() # Return empty if model not built

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