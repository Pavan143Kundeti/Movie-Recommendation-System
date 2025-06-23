# 🎬 Professional Movie Recommendation System

A full-featured, production-ready movie recommendation system built with **Streamlit**, **Python**, **MySQL**, and **Machine Learning**. This project demonstrates advanced web application development with real-time features, analytics, and professional UI/UX.

## ✨ Features

### 🔐 User Authentication & Management
- **Secure login/signup** with hashed passwords
- **Role-based access control** (User/Admin)
- **Session management** with Streamlit
- **User activity logging** for all actions

### 📊 Admin Dashboard
- **Real-time metrics** using `st.metric()`
- **Interactive charts** with Plotly
- **Analytics overview**: Total users, movies, watchlist, watched count
- **Genre distribution** visualization
- **Recent activity tracking**
- **Recent uploads timeline**

### 📤 Bulk Upload System
- **CSV file upload** for multiple movies
- **Data validation** and error handling
- **Preview functionality** before upload
- **Progress tracking** and success/error reporting
- **Sample CSV template** provided

### 🎯 Content-Based Recommendation Engine
- **TF-IDF vectorization** for movie content analysis
- **Cosine similarity** for finding similar movies
- **Personalized recommendations** based on viewing history
- **Real-time model building** with caching

### 🔍 Advanced Search & Filtering
- **Search autocomplete** with real-time suggestions
- **Genre-based filtering**
- **Title-based search**
- **Combined search and filter** functionality

### 📱 Mobile-Friendly Design
- **Responsive layout** that adapts to screen size
- **Mobile-optimized** button sizes and text
- **Touch-friendly** interface elements
- **Progressive Web App** features

### 📄 Pagination System
- **6 movies per page** for optimal performance
- **Navigation controls** (Previous/Next)
- **Page jumping** functionality
- **Current page indicator**

### 🖼️ Enhanced Movie Display
- **Movie poster display** from URL links
- **Default placeholder images** for missing posters
- **Error handling** for broken image URLs
- **Responsive grid layout** (3 columns on desktop, 2 on mobile)

### 📋 Watchlist & History Management
- **Add/remove movies** from watchlist
- **Mark movies as watched**
- **Viewing history** tracking
- **Data export** functionality (CSV)

### 🔔 Toast Notifications & Alerts
- **Success messages** for all actions
- **Error notifications** with clear messaging
- **Welcome messages** on login
- **Action confirmations**

### 📈 User Activity Logging
- **Comprehensive activity tracking**
- **Timeline display** of recent actions
- **Activity icons** for different action types
- **Timestamp formatting**

### 🧪 Unit Testing
- **Comprehensive test suite** for core functionality
- **Database connection testing**
- **Recommendation logic validation**
- **Data structure validation**

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd OTT
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
1. Create a MySQL database named `movie_db`
2. Create `.streamlit/secrets.toml` file:
```toml
[mysql]
host = "localhost"
user = "your_username"
password = "your_password"
database = "movie_db"
```

### 5. Run the Application
```bash
streamlit run app.py
```

## 📁 Project Structure

```
OTT/
├── app.py                          # Main application file
├── requirements.txt                # Python dependencies
├── sample_movies.csv              # Sample data for bulk upload
├── test_app.py                    # Unit tests
├── README.md                      # Project documentation
├── modules/
│   ├── database.py               # Database operations
│   └── recommender.py            # ML recommendation engine
├── pages/
│   ├── 1_Admin_Panel.py          # Admin dashboard
│   └── 2_My_Profile.py           # User profile page
└── .streamlit/
    └── secrets.toml              # Database credentials
```

## 🎯 Key Features in Detail

### Admin Dashboard
The admin dashboard provides comprehensive analytics:
- **Metrics Cards**: Total users, movies, watchlist items, watched movies
- **Genre Distribution Chart**: Visual representation of movie genres
- **Recent Uploads Timeline**: Track new movie additions
- **Activity Summary**: Recent system activity

### Bulk Upload System
Upload multiple movies efficiently:
1. Prepare CSV file with required columns
2. Upload via admin panel
3. Preview data before confirmation
4. Automatic validation and error reporting
5. Success/failure tracking

### Search Autocomplete
Enhanced search experience:
- Real-time suggestions as you type
- Click-to-search functionality
- Genre and year information in suggestions
- Fast response with database optimization

### Mobile Responsiveness
Professional mobile experience:
- Adaptive column layout (3→2 columns on mobile)
- Touch-friendly buttons and inputs
- Optimized font sizes and spacing
- Collapsible sidebar for mobile

## 🧪 Testing

Run the test suite:
```bash
python test_app.py
```

Tests cover:
- Password hashing functionality
- Movie data structure validation
- Recommendation model building
- Search functionality
- CSV parsing
- Data validation

## 📊 Database Schema

### Tables
1. **users**: User accounts and authentication
2. **movies**: Movie information and metadata
3. **watchlist**: User watchlist relationships
4. **history**: User viewing history
5. **activity_log**: User activity tracking

### Key Features
- **Foreign key relationships** for data integrity
- **Timestamps** for all user actions
- **Indexed fields** for fast searches
- **Enum types** for data consistency

## 🎨 UI/UX Features

### Visual Design
- **Modern, clean interface** with emojis and icons
- **Consistent color scheme** and typography
- **Card-based layout** for movie display
- **Professional spacing** and alignment

### User Experience
- **Intuitive navigation** with sidebar
- **Clear feedback** for all actions
- **Loading states** and progress indicators
- **Error handling** with helpful messages

### Accessibility
- **Keyboard navigation** support
- **Screen reader** friendly
- **High contrast** elements
- **Responsive design** for all devices

## 🔧 Technical Implementation

### Backend Technologies
- **Streamlit**: Web framework and UI
- **MySQL**: Relational database
- **Pandas**: Data manipulation
- **Scikit-learn**: Machine learning
- **Plotly**: Interactive visualizations

### Key Algorithms
- **TF-IDF Vectorization**: Text feature extraction
- **Cosine Similarity**: Content-based recommendations
- **SHA-256 Hashing**: Password security
- **Pagination**: Efficient data loading

### Performance Optimizations
- **Database indexing** for fast queries
- **Caching** for recommendation models
- **Lazy loading** for movie data
- **Connection pooling** for database

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
1. Set up MySQL server
2. Configure environment variables
3. Install dependencies
4. Run with production settings

### Cloud Deployment Options
- **Streamlit Cloud**: Easy deployment
- **Heroku**: Container-based deployment
- **AWS/GCP**: Scalable cloud deployment
- **Docker**: Containerized deployment

## 📈 Future Enhancements

### Planned Features
- **Collaborative filtering** recommendations
- **User ratings and reviews**
- **Advanced analytics** dashboard
- **API endpoints** for external access
- **Real-time notifications**
- **Social features** (sharing, following)

### Technical Improvements
- **Redis caching** for better performance
- **Microservices architecture**
- **GraphQL API**
- **Real-time WebSocket** connections
- **Advanced ML models**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Created as a final year B.Tech project demonstrating:
- Full-stack web development
- Database design and management
- Machine learning integration
- Professional UI/UX design
- Production-ready application development

## 🆕 Recent Features & Fixes (2024)

- **User Movie Cards:** Now show 📋 watchlist and 📝 review counts for every movie.
- **Role-Based UI:** Admin and user features are separated and protected by role.
- **Sidebar Clock:** Real-time clock in sidebar (option for live updating).
- **Profile Images:** Always use default avatars, never crash on None.
- **Auto-Migration:** User table columns (full_name, last_login, etc.) are auto-added on app start.
- **Signup Bugfix:** Signup now works (get_user_by_username added).
- **Image Handling:** Improved error handling for missing/broken images.
- **Admin Panel:** Improved error handling and analytics for watchlist/reviews per movie.
- **Linter/Runtime Fixes:** All known linter and runtime errors fixed for smooth deployment.

---

**🎬 Ready for production deployment and job interviews!** 