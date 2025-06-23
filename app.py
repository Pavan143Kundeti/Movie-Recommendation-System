import streamlit as st
from modules import database, recommender
import pandas as pd
import importlib.util
from modules.localization import get_text
import time
import datetime
import streamlit.components.v1 as components
from decimal import Decimal
import importlib
import os
from collections import Counter

# Configuration for mobile-friendly layout
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide the default Streamlit sidebar navigation
# (Delete the block that sets [data-testid="stSidebarNav"] to display: none;)

# Custom CSS for mobile responsiveness
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stMetric {
            font-size: 0.8rem;
        }
        .stButton > button {
            width: 100%;
            font-size: 0.8rem;
        }
        .stTextInput > div > div > input {
            font-size: 0.9rem;
        }
    }
    
    .movie-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f9f9f9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: box-shadow 0.3s ease-in-out, transform 0.3s ease-in-out;
    }
    
    .movie-card:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transform: translateY(-5px);
    }
    
    .suggestion-item {
        padding: 8px 12px;
        cursor: pointer;
        border-bottom: 1px solid #eee;
    }
    
    .suggestion-item:hover {
        background-color: #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

# --- Fix: Always convert MySQL rows to dicts before using .get() ---
def row_to_dict(row):
    return {k: row[k] for k in row.keys()}

@st.cache_data
def get_filter_data():
    """Caches the filter bounds (years, genres, etc.) to prevent re-querying."""
    return database.get_movie_filter_bounds()

@st.cache_data
def load_and_build_model():
    """
    Loads all movies from the database and builds the recommendation model.
    The cache ensures this runs only when the underlying data changes.
    """
    movies_list = database.get_all_movies()
    if not movies_list:
        return None, None
    movies_df = pd.DataFrame(movies_list)
    recommender.build_recommendation_model(movies_df)
    return movies_df

# --- Fix: Always convert DB rows to dicts in all loops ---
def get_suggestions(search_term):
    suggestions_rows = database.get_movie_suggestions(search_term, limit=5)
    return [row_to_dict(r) for r in suggestions_rows] if suggestions_rows else []

def display_movie_poster(movie_data):
    movie = row_to_dict(movie_data) if movie_data else {}
    poster_url = movie.get('poster_url')
    default_poster = "https://via.placeholder.com/300x450/2E2E2E/FFFFFF?text=🎬+No+Poster"
    
    # A simple check to see if the URL is plausible
    is_valid = poster_url and isinstance(poster_url, str) and poster_url.strip().startswith('http')

    if is_valid:
        st.image(str(poster_url), use_column_width=True)
    else:
            st.image(default_poster, use_column_width=True)

def search_autocomplete():
    """Search with autocomplete suggestions"""
    # Get search term
    search_term = st.text_input(
        "🔍 Search movies...",
        key="search_input",
        placeholder="Type to search movies..."
    )
    
    # Show suggestions if user is typing
    if search_term and len(search_term) >= 2:
        suggestions = get_suggestions(search_term)
        
        if suggestions:
            st.write("**Suggestions:**")
            for suggestion in suggestions:
                title = suggestion.get('title', 'No Title')
                release_year = suggestion.get('release_year', 'N/A')
                genre = suggestion.get('genre', 'Unknown')
                if st.button(
                    f"🎬 {title} ({release_year}) - {genre}",
                    key=f"suggest_{title}",
                    help=f"Click to search for {title}"
                ):
                    st.session_state.search_term = title
                    st.rerun()
    
    return search_term

def display_movie_grid(movies_rows, total_movies, page=1, per_page=12, cols_per_row=4):
    """
    Displays movies in a responsive grid and handles pagination controls.
    This function receives a pre-paginated list of movies.
    """
    movies = [row_to_dict(row) for row in movies_rows] if movies_rows else []
    if not movies:
        st.warning("No movies found matching your criteria.")
        return
        
    # Display movies in grid
    cols = st.columns(cols_per_row)
    
    for i, movie in enumerate(movies):
        col = cols[i % cols_per_row]
        
        with col:
            # Use a custom key for the container to ensure it's unique
            with st.container(border=True):
                # Movie poster
                display_movie_poster(movie)
                # Movie title
                st.markdown(f"**{movie.get('title', 'No Title')}**")
                # Movie details
                st.caption(f"🎬 {movie.get('type', 'Unknown')} | 🎭 {movie.get('genre', 'Unknown')} | 📅 {movie.get('release_year', 'N/A')}")
                # --- Watchlist and Reviews Counts ---
                movie_id = movie.get('id')
                watchlist_count = database.get_watchlist_count(movie_id) if movie_id else 0
                review_count = database.get_review_count(movie_id) if movie_id else 0
                st.caption(f"📋 Watchlist: {watchlist_count} | 📝 Reviews: {review_count}")
                # Watchlist & History Buttons
                user_id = st.session_state.user.get('id') if st.session_state.user else None
                if movie_id and user_id:
                    # --- RATING DISPLAY ---
                    rating_summary_row = database.get_rating_summary(movie_id)
                    rating_summary = row_to_dict(rating_summary_row) if rating_summary_row else {}
                    avg_rating = rating_summary.get('average_rating', 0.0)
                    review_count = rating_summary.get('review_count', 0)
                    # Fix: Only convert to float if possible and safe
                    if isinstance(avg_rating, (int, float, str)):
                        try:
                            avg_rating_float = float(avg_rating)
                        except (TypeError, ValueError):
                            avg_rating_float = 0.0
                    else:
                        avg_rating_float = 0.0
                    if avg_rating_float > 0:
                        st.markdown(f"**⭐ {avg_rating_float:.1f}/5** ({review_count} reviews)")
                    else:
                        st.caption(get_text("no_reviews") or "No reviews yet")
                    in_watchlist = database.is_in_watchlist(user_id, movie_id)
                    button_col1, button_col2 = st.columns(2)
                    with button_col1:
                        if in_watchlist:
                            if st.button(get_text("watchlist_remove") or "➖ Watchlist", key=f"wl_{movie_id}", use_container_width=True):
                                database.remove_from_watchlist(user_id, movie_id)
                                st.toast(f"Removed '{movie.get('title', 'No Title')}' from watchlist!", icon="📋")
                                st.rerun()
                        else:
                            if st.button(get_text("watchlist_add") or "➕ Watchlist", key=f"wl_{movie_id}", use_container_width=True):
                                database.add_to_watchlist(user_id, movie_id)
                                st.toast(f"Added '{movie.get('title', 'No Title')}' to watchlist!", icon="📋")
                                st.rerun()
                    with button_col2:
                        # Check if a session is currently active for THIS movie
                        is_watching = st.session_state.get('active_session_movie_id') == movie_id
                        if is_watching:
                            # Show stop button
                            if st.button("⏹️ Stop", key=f"stop_{movie_id}", use_container_width=True):
                                session_id = st.session_state.get('active_session_id')
                                if session_id:
                                    database.end_watch_session(session_id)
                                    database.add_to_history(user_id, movie_id)
                                    st.toast(f"Finished watching '{movie.get('title', 'No Title')}'!", icon="✅")
                                    # Clear session state
                                    del st.session_state['active_session_id']
                                    del st.session_state['active_session_movie_id']
                                    st.rerun()
                        else:
                            # Show watch now button
                            if st.button("▶️ Watch Now", key=f"watch_{movie_id}", use_container_width=True):
                                # End any other active session before starting a new one
                                if 'active_session_id' in st.session_state:
                                    database.end_watch_session(st.session_state.active_session_id)
                                    st.toast("Stopped previous movie session.", icon="⏹️")
                                # Start a new session
                                session_id = database.start_watch_session(user_id, movie_id)
                                if session_id:
                                    st.session_state['active_session_id'] = session_id
                                    st.session_state['active_session_movie_id'] = movie_id
                                    st.toast(f"Started watching '{movie.get('title', 'No Title')}'!", icon="▶️")
                                    st.rerun()
                    # --- REVIEW & DETAILS EXPANDER ---
                    with st.expander(get_text("details_reviews") or "Details & Reviews"):
                        # Movie description
                        description = movie.get('description')
                        st.subheader("Description")
                        if description and description.strip():
                             st.write(description)
                        else:
                            st.write("No description available.")
                        # Cast information
                        cast = movie.get('cast')
                        if cast and cast.strip() and cast != "Unknown":
                            st.caption(f"👥 Cast: {cast}")
                        # Audio Language
                        audio_lang = movie.get('audio_languages')
                        if audio_lang and audio_lang.strip():
                            st.caption(f"🗣️ Audio: {audio_lang}")
                        # --- REVIEW SECTION ---
                        st.subheader("Recent Reviews")
                        reviews_rows = database.get_reviews_for_movie(movie_id)
                        reviews = [row_to_dict(row) for row in reviews_rows] if reviews_rows else []
                        if not reviews:
                            st.write("Be the first to review this movie!")
                        else:
                            for review in reviews:
                                created_at = review.get('created_at')
                                # Fix: Only call strftime if it's a datetime.datetime and not None
                                if created_at is not None and isinstance(created_at, datetime.datetime):
                                    created_at_str = created_at.strftime('%Y-%m-%d')
                                elif created_at is not None and not isinstance(created_at, (str, int, float, Decimal, bytes, set)):
                                    created_at_str = str(created_at)
                                else:
                                    created_at_str = ''
                                st.markdown(f"**{review.get('username', 'Anonymous')}** ({review.get('rating', 'N/A')}⭐) - *{created_at_str}*")
                                st.text(review.get('review', 'No review text.'))
                                st.divider()
                        # Form to add/update a review
                        st.subheader("Add or Update Your Review")
                        with st.form(key=f"review_form_{movie_id}", clear_on_submit=True):
                            user_rating = st.slider("Your Rating (1-5 ⭐)", 1, 5, 3, key=f"rating_{movie_id}")
                            user_review = st.text_area("Your Review", max_chars=250, placeholder="What did you think?", key=f"review_text_{movie_id}")
                            submit_review = st.form_submit_button("Submit Your Review")
                            if submit_review:
                                if database.add_or_update_review(movie_id, user_id, user_rating, user_review):
                                    st.toast("Your review has been submitted!", icon="🎉")
                                    st.rerun()
                                else:
                                    st.error("Failed to submit review. Please try again.")
                # Add some spacing between movie cards
                st.markdown("---")

    # --- PAGINATION CONTROLS ---
    total_pages = (total_movies + per_page - 1) // per_page
    
    if total_pages > 1:
        st.divider()
        
        # Display current page info
        st.write(f"Page **{page}** of **{total_pages}** (Total movies: **{total_movies}**)")
        
        cols = st.columns([1, 1, 1, 5, 1, 1, 1])

        if page > 1:
            if cols[0].button("⏮️ First", use_container_width=True):
                st.session_state.current_page = 1
                st.rerun()
            if cols[1].button("⬅️ Previous", use_container_width=True):
                st.session_state.current_page = page - 1
                st.rerun()
        
        if page < total_pages:
            if cols[5].button("Next ➡️", use_container_width=True):
                st.session_state.current_page = page + 1
                st.rerun()
            if cols[6].button("Last ⏭️", use_container_width=True):
                st.session_state.current_page = total_pages
                st.rerun()
        
        # Page jump in the middle
        with cols[3]:
            page_jump = st.number_input(
                "Go to page:", 
                min_value=1, 
                max_value=total_pages, 
                value=page, 
                key='page_jump'
            )
            if page_jump != page:
                st.session_state.current_page = page_jump
                st.rerun()

def login_page():
    st.header("🔐 Login")

    with st.form(key="login_form"):
        username_or_email = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        
        submitted = st.form_submit_button("Login")

        if submitted:
            user_row, message = database.authenticate_user(username_or_email, password)
            if user_row:
                st.session_state.logged_in = True
                st.session_state.user = row_to_dict(user_row)
                st.toast(f"Welcome back, {st.session_state.user.get('username', 'User')}!", icon="👋")
                st.rerun() 
            else:
                st.error(message)
    
    st.divider()
    
    # Use markdown for robust navigation links
    st.markdown("""
        <div style="display: flex; justify-content: space-around;">
            <div style="text-align: center;">
                <p>Don't have an account?</p>
                <a href="/Signup" target="_self" style="text-decoration: none;">
                    <button style="width: 150px; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">Sign Up Here</button>
                </a>
            </div>
            <div style="text-align: center;">
                <p>Forgot your password?</p>
                <a href="/Reset_Password" target="_self" style="text-decoration: none;">
                    <button style="width: 150px; padding: 10px; border-radius: 5px; border: 1px solid #ccc;">Reset Here</button>
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- THEME AND STYLING ---
def apply_theme():
    """Applies custom CSS based on the selected theme in session state."""
    if 'theme' not in st.session_state:
        st.session_state.theme = "Light" # Default theme

    light_theme = {
        "--background-color": "#FFFFFF",
        "--primary-text-color": "#262730",
        "--secondary-text-color": "#52575C",
        "--card-background-color": "#F9F9F9",
        "--card-border-color": "#DDDDDD",
        "--card-shadow": "rgba(0,0,0,0.1)",
    }

    dark_theme = {
        "--background-color": "#0E1117",
        "--primary-text-color": "#FAFAFA",
        "--secondary-text-color": "#A0A0A0",
        "--card-background-color": "#161B22",
        "--card-border-color": "#30363D",
        "--card-shadow": "rgba(255,255,255,0.1)",
    }
    
    theme = dark_theme if st.session_state.theme == "Dark" else light_theme

    # Construct the CSS string with variables
    css_variables = " ".join([f"{key}: {value};" for key, value in theme.items()])
    
    st.markdown(f"""
    <style>
        :root {{ {css_variables} }}

        .stApp {{
            background-color: var(--background-color);
            color: var(--primary-text-color);
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: var(--primary-text-color);
        }}
        .stMarkdown, p, .st-emotion-cache-16idsys p {{
             color: var(--primary-text-color);
        }}
        .st-emotion-cache-16txtl3 {{
            color: var(--secondary-text-color);
        }}
        .movie-card {{
            background-color: var(--card-background-color);
            border: 1px solid var(--card-border-color);
            box-shadow: 0 2px 4px var(--card-shadow);
        }}
        .st-emotion-cache-1y4p8pa, .st-emotion-cache-1v0mbdj, .st-emotion-cache-1kyxreq, .st-emotion-cache-1xujw88, .st-emotion-cache-134p3na {{
             background-color: var(--card-background-color) !important;
        }}
    </style>
    """, unsafe_allow_html=True)

def advanced_filter_ui(filter_data):
    """Renders the advanced filter UI and returns the selected filter values."""
    with st.expander("🔍 Advanced Filters & Sort", expanded=True):
        
        # --- Filter Widgets ---
        col1, col2 = st.columns(2)
        with col1:
            st.multiselect("Genre(s)", filter_data['genres'], key='filter_genres')
            st.radio("Content Type", ["All", "Movie", "Series"], key='filter_type', horizontal=True)
            st.slider("Release Year", min_value=filter_data['min_year'], max_value=filter_data['max_year'], value=(filter_data['min_year'], filter_data['max_year']), key='filter_year_range')
        
        with col2:
            st.multiselect("Audio Language(s)", filter_data['audio_languages'], key='filter_audio_languages')
            st.radio("Minimum Rating", ["All", "4+ stars", "3+ stars", "Below 3 stars"], key='filter_rating', horizontal=True)
            st.selectbox("Sort By", ["Popularity", "Rating", "Newest"], key='filter_sort_by')
            
        # --- Action Buttons ---
        st.divider()
        col_btn1, col_btn2, _ = st.columns([1, 1, 5])
        
        if col_btn1.button("🔄 Reset Filters"):
            keys_to_reset = ['filter_genres', 'filter_type', 'filter_year_range', 'filter_audio_languages', 'filter_rating', 'filter_sort_by', 'search_term', 'current_page']
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        # The search button is implicit, as widgets trigger a rerun on change.
        # This button is here for user clarity if needed.
        col_btn2.button("Apply Filters", type="primary")

def display_value(val, default="N/A"):
    if val is None or str(val).strip() == "" or str(val).lower() == "none":
        return default
    return str(val)

def main():
    """Main function to run the Streamlit application."""

    # Initialize session state for filters
    filter_keys = {
        'search_term': "",
        'filter_genres': [],
        'filter_type': "All",
        'filter_year_range': (get_filter_data()['min_year'], get_filter_data()['max_year']),
        'filter_audio_languages': [],
        'filter_rating': "All",
        'filter_sort_by': "Popularity"
    }
    for key, default_value in filter_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # Initialize other session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'active_session_id' not in st.session_state:
        st.session_state.active_session_id = None
    if 'active_session_movie_id' not in st.session_state:
        st.session_state.active_session_movie_id = None
    if 'theme' not in st.session_state:
        st.session_state.theme = "Light"

    # Apply the selected theme
    apply_theme()
        
    # --- DATABASE INITIALIZATION ---
    try:
        # Hide the success message after first run
        with st.spinner("Initializing database..."):
            database.init_database() # Using init_database for consistency
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return # Stop the app if DB fails

    # --- APP ROUTING ---
    if st.session_state.logged_in and st.session_state.user:
        # --- LOGGED-IN VIEW ---
        theme_choice = st.sidebar.radio('Theme', ['Light', 'Dark'], index=0 if st.session_state.theme == 'Light' else 1)
        if theme_choice != st.session_state.theme:
            st.session_state.theme = theme_choice
            st.rerun()
        # Call the custom sidebar from modules/sidebar.py
        # profile_sidebar()

        # Modern, smooth, and fast sidebar user profile section
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background: #f8fafc;
                border-radius: 16px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.07);
                padding: 1.5rem 1rem 1rem 1rem;
                margin: 0.5rem;
            }
            .sidebar-profile-pic {
                border-radius: 50%;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                margin-bottom: 0.5rem;
            }
            .sidebar-username {
                font-weight: 600;
                font-size: 1.1rem;
                margin-bottom: 0.2rem;
            }
            .sidebar-email {
                font-size: 0.9rem;
                color: #666;
                margin-bottom: 0.5rem;
            }
            .sidebar-section {
                margin-bottom: 1.2rem;
            }
            .sidebar-btn {
                width: 100%;
                margin-bottom: 0.3rem;
                border-radius: 8px !important;
                font-size: 1rem !important;
            }
            </style>
        """, unsafe_allow_html=True)

        with st.sidebar:
            # Real-time clock at the top (live updating)
            import datetime, time
            clock_placeholder = st.empty()
            for _ in range(1):  # Show once on initial render
                now = datetime.datetime.now()
                clock_placeholder.markdown(f'<div style="text-align:center;font-size:1.1rem;font-weight:600;margin-bottom:0.5rem;">🕒 {now.strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)
            # If you want a truly live clock, uncomment below (will refresh the sidebar every second, but may cause reruns):
            # while True:
            #     now = datetime.datetime.now()
            #     clock_placeholder.markdown(f'<div style="text-align:center;font-size:1.1rem;font-weight:600;margin-bottom:0.5rem;">🕒 {now.strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)
            #     time.sleep(1)

            st.markdown('<div class="sidebar-section" style="text-align:center;">', unsafe_allow_html=True)
            st.image(
                'https://ui-avatars.com/api/?name=' + st.session_state.user.get('username', 'User'),
                width=80,
                output_format="auto",
                caption="",
                use_column_width=False
            )
            st.markdown(f'<div class="sidebar-username">{st.session_state.user.get("username", "N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="sidebar-email">{st.session_state.user.get("email", "N/A")}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.write(f"**Full Name:** {display_value(st.session_state.user.get('full_name'))}")
            st.write(f"**Account Type:** {'Admin' if st.session_state.user.get('is_admin') or st.session_state.user.get('role') == 'admin' else 'User'}")
            st.write(f"**Date Joined:** {display_value(st.session_state.user.get('date_joined'))}")
            st.write(f"**Last Login:** {display_value(st.session_state.user.get('last_login'))}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            if st.button("🏠 Dashboard", key="sidebar_dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
            if st.button("✏️ Edit Profile", key="sidebar_edit_profile", use_container_width=True):
                st.session_state.page = "edit_profile"
            if st.button("🔐 Change Password", key="sidebar_change_password", use_container_width=True):
                st.session_state.page = "change_password"
            if st.button("🕘 Watch History", key="sidebar_history", use_container_width=True):
                st.session_state.page = "history"
            if st.button("📝 My Reviews", key="sidebar_my_reviews", use_container_width=True):
                st.session_state.page = "my_reviews"
            if st.button("🎖️ Achievements", key="sidebar_achievements", use_container_width=True):
                st.session_state.page = "achievements"
            if st.button("🖼️ Edit Profile", key="sidebar_profile_custom", use_container_width=True):
                st.session_state.page = "profile_custom"
            if st.button("▶️ Continue Watching", key="sidebar_continue", use_container_width=True):
                st.session_state.page = "continue_watching"
            # Only show stats for users, not admins
            if not (st.session_state.user.get('is_admin') or st.session_state.user.get('role') == 'admin'):
                if st.button("📊 My Stats", key="sidebar_stats", use_container_width=True):
                    st.session_state.page = "user_stats"
            # Only show admin panel for admins
            if st.session_state.user.get('is_admin') or st.session_state.user.get('role') == 'admin':
                if st.button("🛡️ Admin Panel", key="sidebar_admin_panel", use_container_width=True):
                    st.session_state.page = "admin_panel"
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            theme_choice = st.radio('Theme', ['Light', 'Dark'], index=0 if st.session_state.theme == 'Light' else 1, key="sidebar_theme_radio")
            if theme_choice != st.session_state.theme:
                st.session_state.theme = theme_choice
                st.rerun()
            if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # --- PAGE SWITCHING LOGIC ---
        page = st.session_state.get('page', 'dashboard')
        if page == 'profile':
            st.header('👤 My Profile')
            st.write('Profile details and summary go here.')
        elif page == 'edit_profile':
            st.header('✏️ Edit Profile')
            with st.form(key='edit_profile_form'):
                new_username = st.text_input('New Username', value=st.session_state.user.get('username', ''))
                new_email = st.text_input('New Email', value=st.session_state.user.get('email', ''))
                new_full_name = st.text_input('Full Name', value=st.session_state.user.get('full_name', ''))
                submitted = st.form_submit_button('Save Changes')
                if submitted:
                    # Here you would update the user in the database
                    st.success('Profile updated successfully!')
        elif page == 'change_password':
            st.header('🔐 Change Password')
            with st.form(key='change_password_form'):
                old_password = st.text_input('Old Password', type='password')
                new_password = st.text_input('New Password', type='password')
                confirm_password = st.text_input('Confirm New Password', type='password')
                submitted = st.form_submit_button('Change Password')
                if submitted:
                    if new_password != confirm_password:
                        st.error('New passwords do not match.')
                    elif len(new_password) < 6:
                        st.error('Password must be at least 6 characters long.')
                    else:
                        # Here you would update the password in the database
                        st.success('Password changed successfully!')
        elif page == 'view_stats':
            st.header('📊 View Stats')
            st.info('User stats and analytics will be shown here.')
        elif page == 'user_stats':
            st.header('📊 My Stats & Analytics')
            user_id = st.session_state.user.get('id')
            # Personal stats
            user_stats = database.get_user_stats(user_id)
            if user_stats:
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                with kpi1:
                    st.metric('Total Watched', user_stats.get('total_watched', 0))
                with kpi2:
                    st.metric('Reviews Written', user_stats.get('total_reviews', 0))
                with kpi3:
                    st.metric('Avg. Rating Given', f"{user_stats.get('average_rating', 0.0):.2f}")
                with kpi4:
                    st.metric('Member Since', str(user_stats.get('member_since', 'N/A'))[:10])
                st.markdown("---")
                genre = user_stats.get('most_watched_genre', 'N/A')
                st.markdown(f'<div style="background:linear-gradient(90deg,#f9d423,#ff4e50);border-radius:10px;padding:1rem 1.5rem;margin-bottom:1rem;color:#222;font-weight:600;font-size:1.1rem;display:inline-block;">🎬 Most Watched Genre: <span style=\"color:#fff;\">{genre}</span></div>', unsafe_allow_html=True)
            else:
                st.info('No personal stats available yet.')
            st.markdown("---")
            # Global stats (read-only, no admin controls)
            st.subheader('Platform Stats')
            metrics = database.get_dashboard_metrics()
            kpi_cols = st.columns(4)
            kpis = {
                "👥 Total Users": metrics.get('total_users', 0),
                "🎬 Total Movies": metrics.get('total_movies', 0),
                "📋 Watchlist Items": metrics.get('total_watchlist', 0),
                "✅ Watched Movies": metrics.get('total_watched', 0),
            }
            for i, (label, value) in enumerate(kpis.items()):
                with kpi_cols[i]:
                    st.metric(label=label, value=str(value))
            st.markdown("---")
            st.subheader('Top Genres')
            genre_data = metrics.get('movies_by_genre', [])
            if genre_data:
                df = pd.DataFrame(genre_data)
                st.bar_chart(df.set_index('genre')['count'], use_container_width=True)
            st.markdown("---")
            st.subheader('Recent Uploads')
            uploads = metrics.get('recent_uploads', [])
            if uploads:
                st.table(pd.DataFrame(uploads))
        elif page == 'history':
            st.header('🕘 Watch History')
            user_id = st.session_state.user.get('id')
            history_rows = database.get_history(user_id)
            history = [row_to_dict(row) for row in history_rows] if history_rows else []
            if not history:
                st.info('No watch history yet.')
            else:
                # --- Advanced Filters ---
                all_genres = sorted({g for h in history for g in (h.get('genre', '') or '').split(',') if g.strip()})
                min_year = min([h.get('release_year', 1900) or 1900 for h in history])
                max_year = max([h.get('release_year', 1900) or 1900 for h in history])
                with st.expander('🔍 Filter & Search', expanded=True):
                    col1, col2, col3 = st.columns([3,2,2])
                    with col1:
                        search = st.text_input('Search by title, cast, or description...')
                    with col2:
                        selected_genres = st.multiselect('Genre', all_genres)
                    with col3:
                        year_range = st.slider('Year', min_value=min_year, max_value=max_year, value=(min_year, max_year))
                # --- Sorting Dropdown ---
                sort_option = st.selectbox('Sort by', [
                    'Recently Watched',
                    'Oldest Watched',
                    'Most Watched',
                    'Title (A-Z)',
                    'Title (Z-A)'
                ], index=0)
                # --- Filtering ---
                filtered = []
                for h in history:
                    title = h.get('title', '').lower()
                    cast = h.get('cast', '').lower()
                    desc = h.get('description', '').lower() if h.get('description') else ''
                    year = h.get('release_year', 0) or 0
                    genres = [g.strip() for g in (h.get('genre', '') or '').split(',') if g.strip()]
                    if search and not (search.lower() in title or search.lower() in cast or search.lower() in desc):
                        continue
                    if selected_genres and not any(g in genres for g in selected_genres):
                        continue
                    if not (year_range[0] <= year <= year_range[1]):
                        continue
                    filtered.append(h)
                # --- Count how many times each movie was watched ---
                id_counts = Counter([h.get('id') for h in filtered])
                # --- Sorting Logic ---
                if sort_option == 'Recently Watched':
                    filtered.sort(key=lambda h: h.get('watched_at', ''), reverse=True)
                elif sort_option == 'Oldest Watched':
                    filtered.sort(key=lambda h: h.get('watched_at', ''))
                elif sort_option == 'Most Watched':
                    filtered.sort(key=lambda h: id_counts[h.get('id')], reverse=True)
                elif sort_option == 'Title (A-Z)':
                    filtered.sort(key=lambda h: h.get('title', '').lower())
                elif sort_option == 'Title (Z-A)':
                    filtered.sort(key=lambda h: h.get('title', '').lower(), reverse=True)
                st.success(f"{len(filtered)} movies/series in your history.")
                # --- Export Button ---
                if filtered:
                    export_df = pd.DataFrame([
                        {
                            'Title': h.get('title', ''),
                            'Year': h.get('release_year', ''),
                            'Genre': h.get('genre', ''),
                            'Cast': h.get('cast', ''),
                            'Watched At': h.get('watched_at', ''),
                            'Times Watched': id_counts[h.get('id')]
                        }
                        for h in filtered
                    ])
                    st.download_button(
                        label='⬇️ Export History as CSV',
                        data=export_df.to_csv(index=False),
                        file_name='watch_history.csv',
                        mime='text/csv',
                        use_container_width=True
                    )
                # --- Display in a modern card grid ---
                per_row = 2 if st.session_state.get('is_mobile', False) else 3
                for i in range(0, len(filtered), per_row):
                    cols = st.columns(per_row)
                    for j, h in enumerate(filtered[i:i+per_row]):
                        with cols[j]:
                            with st.container(border=True):
                                display_movie_poster(h)
                                st.markdown(f"**{h.get('title', 'No Title')}** ({h.get('release_year', 'N/A')})")
                                st.caption(f"🎭 {h.get('genre', 'Unknown')} | 👥 {h.get('cast', 'Unknown')}")
                                st.caption(f"🗓️ Watched: {h.get('watched_at', '')}")
                                st.caption(f"🔁 Times Watched: {id_counts[h.get('id')]}")
                                # --- Review Button ---
                                review_key = f"review_{h.get('id')}_{i}"
                                if st.button("📝 Write/Edit Review", key=review_key):
                                    st.session_state['review_movie_id'] = h.get('id')
                                    st.session_state['review_movie_title'] = h.get('title', '')
                                # --- Show review form if selected ---
                                if st.session_state.get('review_movie_id') == h.get('id'):
                                    # Fetch existing review if any
                                    existing_reviews = database.get_reviews_for_movie(h.get('id'), limit=100)
                                    my_review = None
                                    for r in existing_reviews:
                                        if r.get('username') == st.session_state.user.get('username'):
                                            my_review = r
                                            break
                                    with st.form(key=f'review_form_{h.get("id")}_{i}'):
                                        user_rating = st.slider("Your Rating (1-5 ⭐)", 1, 5, int(my_review.get('rating', 3)) if my_review else 3)
                                        user_review = st.text_area("Your Review", max_chars=250, value=my_review.get('review', '') if my_review else "", placeholder="What did you think?")
                                        submit_review = st.form_submit_button("Submit Review")
                                        if submit_review:
                                            database.add_or_update_review(h.get('id'), user_id, user_rating, user_review)
                                            st.toast("Your review has been submitted!", icon="🎉")
                                            del st.session_state['review_movie_id']
                                            st.rerun()
                                if st.button(f"▶️ Rewatch", key=f"rewatch_{h.get('id')}_{i}"):
                                    st.session_state['active_session_movie_id'] = h.get('id')
                                    st.toast(f"Started watching '{h.get('title', 'No Title')}' again!", icon="▶️")
                                    st.rerun()
        elif page == 'my_reviews':
            st.header('📝 My Reviews')
            user_id = st.session_state.user.get('id')
            reviews = database.get_reviews_for_user(user_id)
            if not reviews:
                st.info('No reviews yet.')
            else:
                for r in reviews:
                    with st.container(border=True):
                        st.markdown(f"**{r.get('title', 'No Title')}** ({r.get('release_year', 'N/A')})")
                        st.caption(f"Your Rating: {r.get('rating', 'N/A')}⭐ | Genre: {r.get('genre', 'Unknown')} | Date: {r.get('created_at', '')}")
                        st.text(r.get('review', 'No review text.'))
                        col1, col2 = st.columns([1,1])
                        with col1:
                            if st.button(f"✏️ Edit", key=f"edit_review_{r.get('id')}"):
                                st.session_state['edit_review_id'] = r.get('id')
                                st.session_state['edit_review_text'] = r.get('review', '')
                                st.session_state['edit_review_rating'] = r.get('rating', 3)
                        with col2:
                            if st.button(f"🗑️ Delete", key=f"delete_review_{r.get('id')}"):
                                st.warning('Delete review feature not implemented yet.')
                # Edit review form
                if 'edit_review_id' in st.session_state:
                    with st.form(key='edit_review_form'):
                        new_text = st.text_area('Edit your review', value=st.session_state.get('edit_review_text', ''))
                        new_rating = st.slider('Edit your rating', 1, 5, int(st.session_state.get('edit_review_rating', 3)))
                        submit = st.form_submit_button('Save Changes')
                        if submit:
                            # Find the movie_id for this review
                            review_obj = next((x for x in reviews if x['id'] == st.session_state['edit_review_id']), None)
                            if review_obj:
                                movie_id = review_obj.get('id')
                                database.add_or_update_review(movie_id, user_id, new_rating, new_text)
                                st.toast('Review updated!', icon='✅')
                            del st.session_state['edit_review_id']
                            st.rerun()
        elif page == 'achievements':
            st.header('🎖️ Achievements & Badges')
            user_id = st.session_state.user.get('id')
            badges = database.get_user_badges(user_id)
            if not badges:
                st.info('No badges earned yet. Start watching and reviewing!')
            else:
                for b in badges:
                    st.markdown(f"**🏅 {b.get('name', 'Badge')}**: {b.get('description', '')}")
        elif page == 'profile_custom':
            st.header('🖼️ Edit Profile')
            user = st.session_state.user
            with st.form(key='profile_custom_form'):
                new_pic = st.text_input('Profile Picture URL', value=user.get('profile_pic', ''))
                new_bio = st.text_area('Short Bio', value=user.get('bio', ''))
                fav_genres = st.text_input('Favorite Genres (comma separated)', value=','.join(user.get('favorite_genres', [])) if user.get('favorite_genres') else user.get('favorite_genres', ''))
                submit = st.form_submit_button('Save Changes')
                if submit:
                    database.update_user_profile_custom(user['id'], new_pic, new_bio, fav_genres)
                    st.session_state.user['profile_pic'] = new_pic
                    st.session_state.user['bio'] = new_bio
                    st.session_state.user['favorite_genres'] = [g.strip() for g in fav_genres.split(',') if g.strip()]
                    st.toast('Profile updated!', icon='✅')
                    st.rerun()
        elif page == 'continue_watching':
            st.header('▶️ Continue Watching')
            user_id = st.session_state.user.get('id')
            unfinished = database.get_continue_watching(user_id)
            if not unfinished:
                st.info('No unfinished movies or series.')
            else:
                per_row = 2 if st.session_state.get('is_mobile', False) else 3
                for i in range(0, len(unfinished), per_row):
                    cols = st.columns(per_row)
                    for j, u in enumerate(unfinished[i:i+per_row]):
                        with cols[j]:
                            with st.container(border=True):
                                display_movie_poster(u)
                                st.markdown(f"**{u.get('title', 'No Title')}** ({u.get('release_year', 'N/A')})")
                                st.caption(f"🎭 {u.get('genre', 'Unknown')} | 👥 {u.get('cast', 'Unknown')}")
                                if st.button(f"▶️ Resume", key=f"resume_{u.get('id')}_{i}"):
                                    st.session_state['active_session_movie_id'] = u.get('id')
                                    st.toast(f"Resumed watching '{u.get('title', 'No Title')}'!", icon="▶️")
                                    st.rerun()
        elif page == 'admin_panel':
            # Only allow admins to access admin panel
            if st.session_state.user.get('is_admin') or st.session_state.user.get('role') == 'admin':
            admin_panel_path = os.path.join('pages', '1_Admin_Panel.py')
            if os.path.exists(admin_panel_path):
                spec = importlib.util.spec_from_file_location('admin_panel', admin_panel_path)
                if spec is not None and spec.loader is not None:
                    admin_panel = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(admin_panel)
                    if hasattr(admin_panel, 'main'):
                        admin_panel.main()
                    else:
                        st.header('🛡️ Admin Panel')
                        st.write('Admin Panel page loaded, but no main() function found.')
                else:
                    st.header('🛡️ Admin Panel')
                    st.write('Could not load Admin Panel module spec or loader.')
            else:
                st.header('🛡️ Admin Panel')
                st.write('Admin Panel page not found.')
            else:
                st.error('🚫 You do not have permission to access the Admin Panel.')
        elif page == 'dashboard' or True:
            # Default dashboard/main page
            st.title(get_text("page_title") or "Movie Recommendation System")
            st.write((get_text("welcome_message") or "Welcome, {username}! Explore our collection of movies and series.").format(username=st.session_state.user.get('username', 'user')))
            
            # --- Load data and build model ---
            movies_df = load_and_build_model()

            if movies_df is None:
                st.warning("No movies in database to build recommendation model.")
            else:
                # --- Recommended for You Section ---
                st.header(get_text("recommended_for_you") or "✨ Recommended for You")
                user_id = st.session_state.user.get('id')
                if user_id:
                    user_history_rows = database.get_history(user_id)
                    user_history = [row_to_dict(row) for row in user_history_rows] if user_history_rows else []
                    if not user_history:
                        st.info("Watch some movies to get personalized recommendations!")
                    else:
                        last_watched_movie = user_history[0]
                        last_watched_movie_title = last_watched_movie.get('title')
                        if last_watched_movie_title:
                            recommendations_df = recommender.get_recommendations(last_watched_movie_title)
                            
                            # Get a list of movie IDs the user is not interested in
                            excluded_movie_ids = database.get_user_recommendation_feedback_ids(user_id)

                            if recommendations_df is not None and not recommendations_df.empty:
                                # Filter out the movies the user is not interested in
                                filtered_recs_df = recommendations_df[~recommendations_df['id'].isin(excluded_movie_ids)]

                                if filtered_recs_df.empty:
                                    st.info("We've run out of new recommendations for now. Check back later!")
                                else:
                                    st.write((get_text("because_you_watched") or "Because you watched **{movie_title}**:").format(movie_title=last_watched_movie_title))
                                    rec_cols = st.columns(5)
                                    for i, (_, rec_row) in enumerate(filtered_recs_df.head(5).iterrows()):
                                        rec = rec_row.to_dict()
                                        with rec_cols[i]:
                                            with st.container():
                                                display_movie_poster(rec)
                                                st.markdown(f"**{rec.get('title', 'N/A')}**")
                                                st.caption(f"📅 {rec.get('release_year', 'N/A')}")
                                                rec_id = rec.get('id')
                                                if st.button("Not Interested", key=f"rec_not_interested_{rec_id}", use_container_width=True):
                                                    database.add_recommendation_feedback(user_id, rec_id)
                                                    st.toast(f"We won't recommend '{rec.get('title', 'N/A')}' anymore.", icon="👍")
                                                    st.rerun()
                            else:
                                st.info("Could not find recommendations based on your last watched movie.")
                st.divider()

                # --- Trending Now Section ---
                st.header("🔥 Trending Now")
                trending_movies_rows = database.get_trending_movies(limit=10)
                trending_movies = [row_to_dict(row) for row in trending_movies_rows] if trending_movies_rows else []
                if trending_movies:
                    trending_cols = st.columns(5)
                    for i, movie in enumerate(trending_movies[:5]):
                         with trending_cols[i]:
                            with st.container(border=True):
                                display_movie_poster(movie)
                                st.markdown(f"**{movie.get('title', 'N/A')}**")
                                st.caption(f"📅 {movie.get('release_year', 'N/A')}")
                else:
                    st.info("Trending movie data is not available at the moment.")
                st.divider()

                # --- Search and Filter UI ---
                filter_data = get_filter_data()
                with st.expander("🔍 Advanced Filters & Sort", expanded=True):
                    filter_cols = st.columns([2, 2, 2, 2, 2, 2])
                    # Search bar with autocomplete
                    with filter_cols[0]:
                        search_term = st.text_input(
                            "Search by title, cast, or description...",
                            value=st.session_state.get('search_term', ''),
                            key="search_term_input",
                            placeholder="Type to search..."
                        )
                        # Autocomplete suggestions
                        suggestions = []
                        if search_term and len(search_term) >= 2:
                            suggestions = get_suggestions(search_term)
                            if suggestions:
                                for suggestion in suggestions:
                                    if st.button(f"{suggestion.get('title', '')} ({suggestion.get('release_year', '')})", key=f"suggestion_{suggestion.get('title', '')}"):
                                        st.session_state['search_term'] = suggestion.get('title', '')
                                        st.rerun()
                    # Genre filter
                    with filter_cols[1]:
                        genres = st.multiselect("Genre(s)", filter_data['genres'], default=st.session_state.get('filter_genres', []), key='filter_genres')
                    # Year range filter
                    with filter_cols[2]:
                        year_range = st.slider(
                            "Release Year",
                            min_value=filter_data['min_year'],
                            max_value=filter_data['max_year'],
                            value=st.session_state.get('filter_year_range', (filter_data['min_year'], filter_data['max_year'])),
                            key='filter_year_range'
                        )
                    # Audio language filter
                    with filter_cols[3]:
                        audio_languages = st.multiselect("Audio Language(s)", filter_data['audio_languages'], default=st.session_state.get('filter_audio_languages', []), key='filter_audio_languages')
                    # Rating filter
                    with filter_cols[4]:
                        rating = st.radio("Rating", ["All", "4+ stars", "3+ stars", "Below 3 stars"], index=["All", "4+ stars", "3+ stars", "Below 3 stars"].index(st.session_state.get('filter_rating', 'All')), key='filter_rating')
                    # Type filter
                    with filter_cols[5]:
                        movie_type = st.radio("Type", ["All", "Movie", "Series"], index=["All", "Movie", "Series"].index(st.session_state.get('filter_type', 'All')), key='filter_type')
                    # Sorting
                    sort_by = st.selectbox("Sort By", ["Popularity", "Rating", "Newest"], index=["Popularity", "Rating", "Newest"].index(st.session_state.get('filter_sort_by', 'Popularity')), key='filter_sort_by')
                    # Reset button
                    if st.button("🔄 Reset Filters"):
                        keys_to_reset = ['filter_genres', 'filter_type', 'filter_year_range', 'filter_audio_languages', 'filter_rating', 'filter_sort_by', 'search_term', 'current_page']
                        for key in keys_to_reset:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()

                # --- Process filter values for the backend ---
                rating_map = {
                    "4+ stars": "4+",
                    "3+ stars": "3+",
                    "Below 3 stars": "<3"
                }
                sort_map = {
                    "Popularity": "popularity",
                    "Rating": "rating",
                    "Newest": "year"
                }
                # --- Fetch and Display Movies based on search/filter ---
                PER_PAGE = 6
                current_page = st.session_state.get('current_page', 1)
                movies, total_movies = database.get_movies_paginated(
                    page=current_page,
                    per_page=PER_PAGE,
                    query=st.session_state.get('search_term', ''),
                    movie_type=st.session_state.get('filter_type', None) if st.session_state.get('filter_type', 'All') != 'All' else None,
                    genres=st.session_state.get('filter_genres', []),
                    year_range=st.session_state.get('filter_year_range', (filter_data['min_year'], filter_data['max_year'])),
                    rating_filter=rating_map.get(st.session_state.get('filter_rating', 'All')),
                    audio_languages=st.session_state.get('filter_audio_languages', []),
                    sort_by=sort_map.get(st.session_state.get('filter_sort_by', 'Popularity'), 'popularity')
                )
                st.success(f"{total_movies} movies found matching your criteria!")
                st.header((get_text("browse_all") or "📺 Browse All Movies & Series ({count} found)").format(count=total_movies))
                # --- Movie Grid ---
                def movie_grid(movies, per_row=3):
                    if not movies:
                        st.warning("No movies found matching your criteria.")
                        return
                    for i in range(0, len(movies), per_row):
                        cols = st.columns(per_row)
                        for j, movie in enumerate(movies[i:i+per_row]):
                            with cols[j]:
                                with st.container(border=True):
                                    display_movie_poster(movie)
                                    st.markdown(f"**{movie.get('title', 'No Title')}**")
                                    st.caption(f"🎬 {movie.get('type', 'Unknown')} | 🎭 {movie.get('genre', 'Unknown')} | 📅 {movie.get('release_year', 'N/A')}")
                                    st.caption(f"👥 {movie.get('cast', 'Unknown')}")
                movie_grid([row_to_dict(row) for row in movies], per_row=3)
                # --- Pagination Controls ---
                total_pages = (total_movies + PER_PAGE - 1) // PER_PAGE
                if total_pages > 1:
                    st.divider()
                    st.write(f"Page **{current_page}** of **{total_pages}** (Total movies: **{total_movies}**)")
                    cols = st.columns([1, 1, 1, 5, 1, 1, 1])
                    if current_page > 1:
                        if cols[0].button("⏮️ First", use_container_width=True):
                            st.session_state.current_page = 1
                            st.rerun()
                        if cols[1].button("⬅️ Previous", use_container_width=True):
                            st.session_state.current_page = current_page - 1
                            st.rerun()
                    if current_page < total_pages:
                        if cols[5].button("Next ➡️", use_container_width=True):
                            st.session_state.current_page = current_page + 1
                            st.rerun()
                        if cols[6].button("Last ⏭️", use_container_width=True):
                            st.session_state.current_page = total_pages
                            st.rerun()
                    with cols[3]:
                        page_jump = st.number_input(
                            "Go to page:", 
                            min_value=1, 
                            max_value=total_pages, 
                            value=current_page, 
                            key='page_jump'
                        )
                        if page_jump != current_page:
                            st.session_state.current_page = page_jump
                            st.rerun()

    else:
        # --- LOGIN VIEW ---
        login_page()

if __name__ == "__main__":
    main()