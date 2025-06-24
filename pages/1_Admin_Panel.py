import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules import database, tmdb
from app import load_and_build_model
import io
import os

# Modern Admin Panel Sidebar UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #f8fafc 60%, #e0e7ef 100%);
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.09);
        padding: 2rem 1.2rem 1.2rem 1.2rem;
        margin: 0.7rem;
        font-family: 'Inter', sans-serif;
    }
    .admin-sidebar-section {
        margin-bottom: 1.5rem;
    }
    .admin-profile-pic {
        border-radius: 50%;
        box-shadow: 0 2px 12px rgba(0,0,0,0.10);
        margin-bottom: 0.7rem;
        border: 3px solid #e0e7ef;
    }
    .admin-sidebar-username {
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 0.1rem;
        color: #222;
    }
    .admin-sidebar-email {
        font-size: 0.95rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .admin-section-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #3b82f6;
        margin-bottom: 0.5rem;
        margin-top: 0.5rem;
        letter-spacing: 0.01em;
    }
    .admin-btn {
        width: 100%;
        margin-bottom: 0.35rem;
        border-radius: 10px !important;
        font-size: 1.05rem !important;
        background: #f1f5f9;
        color: #222;
        border: none;
        transition: background 0.2s, color 0.2s;
    }
    .admin-btn:hover {
        background: #3b82f6 !important;
        color: #fff !important;
        box-shadow: 0 2px 8px rgba(59,130,246,0.08);
    }
    .admin-active-btn {
        background: #3b82f6 !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="admin-sidebar-section" style="text-align:center;">', unsafe_allow_html=True)
    st.image(
        'https://ui-avatars.com/api/?name=' + st.session_state.user.get('username', 'Admin'),
        width=84,
        output_format="auto",
        caption="",
        use_column_width=False
    )
    st.markdown(f'<div class="admin-sidebar-username">{st.session_state.user.get("username", "N/A")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="admin-sidebar-email">{st.session_state.user.get("email", "N/A")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:1rem;color:#888;">Role: Admin</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="admin-section-title">Management</div>', unsafe_allow_html=True)
    if st.button("👥 User Management", key="admin_user_mgmt", help="Manage users", use_container_width=True):
        st.session_state.admin_section = "user"
    if st.button("🎬 Movie Management", key="admin_movie_mgmt", help="Manage movies", use_container_width=True):
        st.session_state.admin_section = "movie"

    st.markdown('<div class="admin-section-title">Analytics</div>', unsafe_allow_html=True)
    if st.button("📈 Analytics", key="admin_analytics", help="View analytics", use_container_width=True):
        st.session_state.admin_section = "analytics"

    st.markdown('<div class="admin-section-title">Settings</div>', unsafe_allow_html=True)
    if st.button("⚙️ Settings", key="admin_settings", help="Admin settings", use_container_width=True):
        st.session_state.admin_section = "settings"

    st.markdown('<div class="admin-section-title">Session</div>', unsafe_allow_html=True)
    if st.button("🚪 Logout", key="admin_logout", help="Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

def inject_custom_css():
    st.markdown("""
        <style>
            .metric-card {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 16px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
                transition: all 0.3s ease-in-out;
            }
            .metric-card:hover {
                box-shadow: 0 8px 12px rgba(0, 0, 0, 0.06);
                transform: translateY(-2px);
            }
            .st-emotion-cache-1vzeuhh { /* st.tabs inner container */
                border-radius: 8px;
                padding: 1rem;
                background-color: #F8F9FA;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Caching Data Functions ---
def get_cached_dashboard_metrics():
    try:
        return database.get_advanced_dashboard_metrics()
    except Exception as e:
        st.error(f"Error fetching dashboard metrics: {e}")
        return {}

def get_cached_users():
    try:
        return database.get_all_users()
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []

def get_cached_movies():
    try:
        return database.get_all_movies()
    except Exception as e:
        st.error(f"Error fetching movies: {e}")
        return []

def render_dashboard():
    st.header("🚀 Dashboard Overview")
    metrics = get_cached_dashboard_metrics()
    
    if not metrics:
        st.error("Could not load dashboard data.")
        return

    kpi_cols = st.columns(5)
    kpis = {
        "👥 Total Users": (metrics.get('total_users', 0), f"{metrics.get('user_growth_pct', 0)}% vs last week"),
        "🎬 Total Movies": (metrics.get('total_movies', 0), f"{metrics.get('movies_uploaded_today', 0)} today"),
        "📋 Watchlist Items": (metrics.get('total_watchlist', 0), None),
        "✅ Watched Movies": (metrics.get('total_watched', 0), None),
        "⏱️ Avg. Watch Time": (f"{metrics.get('avg_watch_time', 0)} min", None),
    }
    
    for i, (label, (value, delta)) in enumerate(kpis.items()):
        with kpi_cols[i]:
            with st.container():
                st.metric(label=label, value=str(value), delta=delta)

    st.divider()

    chart_cols = st.columns([1, 1])
    with chart_cols[0]:
        signup_data = metrics.get('weekly_signups', [])
        if signup_data:
            df = pd.DataFrame(signup_data)
            fig = px.line(df, x='signup_date', y='count', title='New User Signups (Last 7 Days)')
            st.plotly_chart(fig, use_container_width=True)

        genre_data = metrics.get('genre_distribution', [])
        if genre_data:
            df = pd.DataFrame(genre_data).nlargest(10, 'count')
            fig = px.pie(df, names='genre', values='count', title='Top 10 Movie Genres', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)

    with chart_cols[1]:
        active_user_data = metrics.get('most_active_users', [])
        if active_user_data:
            df = pd.DataFrame(active_user_data)
            fig = px.bar(df, x='username', y='action_count', title='Top 10 Most Active Users')
            st.plotly_chart(fig, use_container_width=True)

    table_cols = st.columns(2)
    with table_cols[0]:
        st.subheader("Newest Users")
        st.dataframe(pd.DataFrame(metrics.get('recent_signups', [])), use_container_width=True)
    with table_cols[1]:
        st.subheader("Admin Activity Log")
        st.dataframe(pd.DataFrame(metrics.get('admin_activity', [])), use_container_width=True)

def render_user_management():
    st.header("👥 User Management")
    all_users = get_cached_users()
    if not all_users:
        st.warning("No users found.")
        return

    users_df = pd.DataFrame(all_users)
    st.dataframe(users_df[['id', 'username', 'email', 'role', 'is_verified', 'date_joined']], use_container_width=True)

    st.divider()
    
    tool_cols = st.columns(3)
    
    with tool_cols[0]:
        with st.form("add_user_form", clear_on_submit=True):
            st.subheader("➕ Add New User")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["user", "admin"], index=0)
            if st.form_submit_button("Create User"):
                if username and email and password and role:
                    if database.add_user(username, email, password):
                        st.toast(f"User '{username}' created!", icon="✅")
                        st.rerun()
                else:
                    st.warning("Please fill out all fields.")

    with tool_cols[1]:
        st.subheader("🛠️ User Actions")
        if all_users:
            # Create a default "None" option
            user_options = {f"{user.get('username', 'N/A')} (ID: {user.get('id', 'N/A')})": str(user.get('id', '')) for user in all_users}
            user_options["-- Select a User --"] = ''
            
            selected_user_display = st.selectbox(
                "Select a user", 
                options=list(user_options.keys()), 
                index=len(user_options) - 1 # Default to "-- Select a User --"
            )
            user_id_to_act_on = user_options.get(str(selected_user_display), '')

            if user_id_to_act_on:
                if st.button("🗑️ Delete User", type="primary", key=f"delete_{user_id_to_act_on}"):
                    if database.delete_user(user_id_to_act_on, st.session_state.user['id']):
                        st.toast("User deleted!", icon="🗑️")
                        st.rerun()

                if st.button("✅ Manually Verify", key=f"verify_{user_id_to_act_on}"):
                    if database.manually_verify_user(user_id_to_act_on):
                        st.toast("User manually verified!", icon="✅")
                        st.rerun()

    with tool_cols[2]:
        st.subheader("🔑 Reset Password")
        if all_users and selected_user_display:
            with st.form("reset_password_form"):
                new_password = st.text_input("New Password", type="password")
                if st.form_submit_button("Reset"):
                    if new_password:
                        if database.reset_user_password_by_admin(user_id_to_act_on, new_password):
                            st.toast("Password has been reset.", icon="🔑")
                        else:
                            st.error("Failed to reset password.")
                    else:
                        st.warning("Password cannot be empty.")

def single_movie_upload():
    with st.form("upload_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title *", placeholder="Enter movie title")
            item_type = st.selectbox("Type *", ["Movie", "Series"])
            genre = st.text_input("Genre", placeholder="Action, Comedy, Drama")
        with col2:
            release_year = st.number_input("Release Year", min_value=1888, max_value=2030, value=2023, step=1)
            audio_languages = st.text_input("Audio Languages", placeholder="e.g., Hindi, English")
        description = st.text_area("Description", placeholder="Enter movie description")
        cast = st.text_input("Cast", placeholder="Actor 1, Actor 2")
        poster_url = st.text_input("Poster Image URL", placeholder="https://example.com/poster.jpg")
        trailer_url = st.text_input("YouTube Trailer URL", placeholder="https://youtube.com/watch?v=...")
        if st.form_submit_button("Upload Movie", type="primary"):
            if all([title, item_type, release_year]):
                if database.add_movie(title, item_type, genre, release_year, description, cast, poster_url, trailer_url, audio_languages, st.session_state.user['id']):
                    st.toast(f"Movie '{title}' uploaded!", icon="🎬")
                    st.rerun()
                else:
                    st.toast("Failed to upload movie.", icon="❌")
            else:
                st.warning("Please fill out all required fields.")

def bulk_upload_section():
    st.info("Required columns: `title`. Optional: `type`, `genre`, `release_year`, `description`, `cast`, `poster_url`, `trailer_url`, `audio_languages`.")
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        if st.button("🚀 Upload from CSV"):
            with st.spinner("Uploading..."):
                success, message = database.bulk_upload_movies(df, st.session_state.user['id'])
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def poster_fix_section():
    st.subheader("Manual Poster URL Fix")
    
    # Search for a movie to fix
    search_movie_title = st.text_input("Search for a movie by title to fix its poster:")
    
    all_movies = get_cached_movies()
    
    if search_movie_title:
        movies_to_fix = [m for m in all_movies if search_movie_title.lower() in str(m.get('title', '')).lower()]
    else:
        # Show movies without valid posters by default
        movies_to_fix = [m for m in all_movies if not str(m.get('poster_url', '')).startswith('http')]

    if movies_to_fix:
        # Create a default "None" option
        movie_options = {f"{movie.get('title', 'N/A')} (ID: {movie.get('id', 'N/A')})": movie.get('id') for movie in movies_to_fix}
        movie_options["-- Select a Movie --"] = None

        selected_movie_title = st.selectbox(
            "Select a movie to fix", 
            options=list(movie_options.keys()),
            index=len(movie_options) - 1 # Default to select
        )
        selected_movie_id = movie_options.get(str(selected_movie_title), '')
        
        if selected_movie_id:
            new_poster_url = st.text_input("New Poster URL", key=f"poster_url_{selected_movie_id}")
            if st.button("Update Poster", key=f"update_poster_{selected_movie_id}"):
                if new_poster_url and new_poster_url.startswith('http'):
                    if database.update_movie_poster(selected_movie_id, new_poster_url):
                        st.toast("Poster updated successfully!", icon="🖼️")
                        st.rerun()
                else:
                    st.error("Failed to update poster.")

def tmdb_population_section():
    """UI for populating the database from TMDB CSV files."""
    st.info("Upload the `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` files.")
    
    col1, col2 = st.columns(2)
    with col1:
        movies_file = st.file_uploader("Upload Movies CSV", type=['csv'])
    with col2:
        credits_file = st.file_uploader("Upload Credits CSV", type=['csv'])

    if st.button("🚀 Start Population"):
        if movies_file is not None and credits_file is not None:
            with st.spinner("Populating database... This may take a few moments."):
                try:
                    movies_df = pd.read_csv(movies_file)
                    credits_df = pd.read_csv(credits_file)
                    
                    user_id = st.session_state.user.get('id')
                    if not user_id:
                        st.error("Could not identify admin user. Aborting.")
                        return

                    success, message = database.populate_from_tmdb_files(movies_df, credits_df, user_id)

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(f"Failed to populate: {message}")
                except Exception as e:
                    st.error(f"An error occurred during file processing: {e}")
        else:
            st.warning("Please upload both CSV files to proceed.")

def render_content_management():
    st.header("🎬 Content Management")
    
    st.subheader("All Movies in Database")
    search_term = st.text_input("Search movies by title...", key="movie_search")
    
    all_movies = get_cached_movies()
    if not all_movies:
        st.warning("No movies found in the database.")
        return
    
    movies_df = pd.DataFrame(all_movies)
    
    # Add watchlist and reviews columns
    movies_df['watchlist'] = movies_df['id'].apply(lambda movie_id: database.get_watchlist_count(movie_id) if hasattr(database, 'get_watchlist_count') else 0)
    movies_df['reviews'] = movies_df['id'].apply(lambda movie_id: database.get_review_count(movie_id) if hasattr(database, 'get_review_count') else 0)
    
    # Ensure all titles are strings before filtering
    movies_df['title_str'] = movies_df['title'].astype(str)
    
    if search_term:
        movies_df = movies_df[movies_df['title_str'].str.contains(search_term, case=False, na=False)]
    
    st.dataframe(movies_df.drop(columns=['title_str']), use_container_width=True)
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["📤 Upload Single Movie", "📦 Bulk Upload via CSV", "🖼️ Fix Movie Poster"])
    
    with tab1:
        single_movie_upload()
    with tab2:
        bulk_upload_section()
    with tab3:
        poster_fix_section()

def render_system_config():
    st.header("⚙️ System & Configuration")
    
    st.subheader("TMDB Data Population")
    tmdb_population_section()

def admin_panel():
    st.title("⚙️ Admin Panel")

    # --- Security Check ---
    if 'user' not in st.session_state or st.session_state.user.get('role') != 'admin':
        st.error("🚫 You do not have permission to access this page.")
        if st.button("Back to Home"):
            st.switch_page("app.py")
        return

    inject_custom_css()

    # Show only the selected admin section content
    section = st.session_state.get("admin_section", "user")  # Default to "user"

    if section == "user":
        st.header("👥 User Management")
        st.info("Manage users here. (Add your user management UI)")
    elif section == "movie":
        st.header("🎬 Movie Management")
        st.info("Manage movies here. (Add your movie management UI)")
    elif section == "analytics":
        st.header("📈 Analytics")
        st.subheader("User Statistics")
        st.metric("Total Users", 123)  # Replace with real data
        st.metric("Active Users", 45)  # Replace with real data

        st.subheader("Movie Statistics")
        st.metric("Total Movies", 200)  # Replace with real data
        st.metric("Most Watched", "Movie Title")  # Replace with real data

        import pandas as pd
        data = pd.DataFrame({
            "Movies": ["Movie A", "Movie B", "Movie C"],
            "Views": [100, 150, 80]
        })
        st.bar_chart(data.set_index("Movies"))
    elif section == "settings":
        st.header("⚙️ Settings")
        st.subheader("Admin Profile Settings")
        with st.form("admin_settings_form"):
            new_email = st.text_input("Change Email", value=st.session_state.user.get("email", ""))
            new_name = st.text_input("Change Name", value=st.session_state.user.get("full_name", ""))
            submitted = st.form_submit_button("Save Settings")
            if submitted:
                st.success("Settings updated!")  # Add real update logic here
    else:
        st.header("Welcome to the Admin Panel")
        st.info("Select a section from the sidebar.")

    # Optionally, reset the section on logout
    if not st.session_state.get("logged_in", False):
        st.session_state["admin_section"] = "user"

    # Remove all sidebar code here. Only render main content.
    # Example: Always show dashboard, user management, content management, and system config in sequence (or as tabs if you want, but not in the sidebar)
    st.header("Admin Dashboard Sections")
    render_dashboard()
    st.divider()
    render_user_management()
    st.divider()
    render_content_management()
    st.divider()
    render_system_config()

def main():
    admin_panel()

if __name__ == "__main__":
    main() 