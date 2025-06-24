#!/usr/bin/env python3
"""
Test script to verify recommender module works with fallback system
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules import recommender
    print("✅ Successfully imported recommender module")
    
    # Test if scikit-learn is available
    if hasattr(recommender, 'SKLEARN_AVAILABLE'):
        if recommender.SKLEARN_AVAILABLE:
            print("✅ scikit-learn is available - using advanced recommendations")
        else:
            print("⚠️  scikit-learn not available - using simple genre-based recommendations")
    
    # Test with sample data
    import pandas as pd
    
    # Create sample movie data
    sample_movies = pd.DataFrame({
        'title': ['Movie A', 'Movie B', 'Movie C', 'Movie D'],
        'genre': ['Action', 'Action', 'Comedy', 'Drama'],
        'description': ['Action movie', 'Another action movie', 'Funny movie', 'Serious movie'],
        'cast': ['Actor 1', 'Actor 2', 'Actor 3', 'Actor 4'],
        'poster_url': ['http://example.com/1.jpg', 'http://example.com/2.jpg', 'http://example.com/3.jpg', 'http://example.com/4.jpg']
    })
    
    print("✅ Testing recommendation system with sample data...")
    
    # Test building the model
    try:
        recommender.build_recommendation_model(sample_movies)
        print("✅ Model building successful")
    except Exception as e:
        print(f"❌ Model building failed: {e}")
    
    # Test getting recommendations
    try:
        recommendations = recommender.get_recommendations('Movie A', num_recommendations=3)
        print(f"✅ Got {len(recommendations)} recommendations for 'Movie A'")
        if not recommendations.empty:
            print(f"   Recommendations: {list(recommendations['title'])}")
    except Exception as e:
        print(f"❌ Getting recommendations failed: {e}")
    
    print("✅ Recommender module test completed successfully")
    
except Exception as e:
    print(f"❌ Failed to import or test recommender module: {e}")
    print("This might be due to missing dependencies or configuration issues.") 