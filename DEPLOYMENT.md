# 🚀 Deployment Guide - Movie Recommendation System

This guide will help you deploy your Movie Recommendation System to various platforms for production use.

## 📋 Prerequisites

Before deployment, ensure you have:
- ✅ Working local application
- ✅ MySQL database setup
- ✅ All dependencies installed
- ✅ Environment variables configured

## 🏠 Local Production Setup

### 1. Environment Configuration

Create a production configuration file:

```bash
# .env (for production)
MYSQL_HOST=your_production_host
MYSQL_USER=your_production_user
MYSQL_PASSWORD=your_production_password
MYSQL_DATABASE=movie_db
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 2. Database Migration

```sql
-- Run these commands on your production MySQL server
CREATE DATABASE movie_db;
USE movie_db;

-- The tables will be created automatically when the app runs
-- But you can also run them manually for verification
```

### 3. Run Production Server

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production settings
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## ☁️ Cloud Deployment Options

### Option 1: Streamlit Cloud (Recommended)

**Pros**: Easy deployment, free tier, automatic updates
**Cons**: Limited customization, database restrictions

#### Steps:
1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Production ready"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Configure secrets in the dashboard

3. **Set Environment Variables**
   ```toml
   # In Streamlit Cloud secrets
   [mysql]
   host = "your-mysql-host"
   user = "your-username"
   password = "your-password"
   database = "movie_db"
   ```

4. **Deploy**
   - Click "Deploy" in Streamlit Cloud
   - Your app will be available at `https://your-app-name.streamlit.app`

### Option 2: Heroku

**Pros**: Full control, PostgreSQL support, scalable
**Cons**: Requires credit card, more complex setup

#### Steps:
1. **Create Heroku App**
   ```bash
   heroku create your-movie-app
   ```

2. **Add PostgreSQL**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

3. **Create Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set MYSQL_HOST=your-host
   heroku config:set MYSQL_USER=your-user
   heroku config:set MYSQL_PASSWORD=your-password
   heroku config:set MYSQL_DATABASE=your-database
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

### Option 3: AWS EC2

**Pros**: Full control, scalable, cost-effective
**Cons**: Requires server management knowledge

#### Steps:
1. **Launch EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - t2.micro for testing, t2.small+ for production
   - Configure security groups (port 8501)

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3 python3-pip python3-venv -y
   ```

3. **Deploy Application**
   ```bash
   # Clone repository
   git clone https://github.com/your-username/OTT.git
   cd OTT
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Setup MySQL**
   ```bash
   # Install MySQL
   sudo apt install mysql-server -y
   
   # Secure installation
   sudo mysql_secure_installation
   
   # Create database and user
   sudo mysql -u root -p
   ```

5. **Run with Systemd**
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/movie-app.service
   ```

   ```ini
   [Unit]
   Description=Movie Recommendation System
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/OTT
   Environment=PATH=/home/ubuntu/OTT/venv/bin
   ExecStart=/home/ubuntu/OTT/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable movie-app
   sudo systemctl start movie-app
   sudo systemctl status movie-app
   ```

### Option 4: Docker Deployment

**Pros**: Consistent environment, easy scaling, portable
**Cons**: Learning curve for Docker

#### Steps:
1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8501

   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8501:8501"
       environment:
         - MYSQL_HOST=db
         - MYSQL_USER=root
         - MYSQL_PASSWORD=password
         - MYSQL_DATABASE=movie_db
       depends_on:
         - db
     
     db:
       image: mysql:8.0
       environment:
         - MYSQL_ROOT_PASSWORD=password
         - MYSQL_DATABASE=movie_db
       volumes:
         - mysql_data:/var/lib/mysql
       ports:
         - "3306:3306"

   volumes:
     mysql_data:
   ```

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

## 🔧 Production Optimizations

### 1. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_genre ON movies(genre);
CREATE INDEX idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX idx_activity_log_created_at ON activity_log(created_at);
```

### 2. Caching Strategy

```python
# Add Redis caching for better performance
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_movies():
    # Implementation
    pass
```

### 3. Security Enhancements

```python
# Add rate limiting
import time
from functools import wraps

def rate_limit(max_requests=100, window=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implementation
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 4. Monitoring and Logging

```python
# Add structured logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## 📊 Performance Monitoring

### 1. Application Metrics

```python
# Add performance monitoring
import time

def monitor_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Log performance metrics
        logging.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
```

### 2. Database Monitoring

```sql
-- Monitor slow queries
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Check query performance
SHOW PROCESSLIST;
EXPLAIN SELECT * FROM movies WHERE title LIKE '%test%';
```

## 🔒 Security Checklist

- [ ] **HTTPS enabled** for all deployments
- [ ] **Environment variables** for sensitive data
- [ ] **Input validation** on all forms
- [ ] **SQL injection prevention** (using parameterized queries)
- [ ] **Rate limiting** implemented
- [ ] **Error handling** without exposing sensitive information
- [ ] **Regular security updates** for dependencies
- [ ] **Database backups** configured
- [ ] **Access logging** enabled

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check MySQL status
   sudo systemctl status mysql
   
   # Check connection
   mysql -u username -p -h hostname
   ```

2. **Port Already in Use**
   ```bash
   # Find process using port
   sudo lsof -i :8501
   
   # Kill process
   sudo kill -9 PID
   ```

3. **Memory Issues**
   ```bash
   # Monitor memory usage
   htop
   
   # Check logs
   tail -f /var/log/syslog
   ```

### Performance Issues

1. **Slow Database Queries**
   - Add database indexes
   - Optimize queries
   - Consider caching

2. **High Memory Usage**
   - Monitor memory usage
   - Optimize data loading
   - Implement pagination

3. **Slow Page Loads**
   - Enable caching
   - Optimize images
   - Use CDN for static assets

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer
- Multiple application instances
- Database replication

### Vertical Scaling
- Increase server resources
- Optimize application code
- Database optimization

### Caching Strategy
- Redis for session storage
- CDN for static assets
- Application-level caching

## 🎯 Deployment Checklist

- [ ] **Code tested** locally
- [ ] **Database migrated** and tested
- [ ] **Environment variables** configured
- [ ] **SSL certificate** installed (if needed)
- [ ] **Domain configured** (if using custom domain)
- [ ] **Monitoring** set up
- [ ] **Backup strategy** implemented
- [ ] **Documentation** updated
- [ ] **Team notified** of deployment

## 📞 Support

For deployment issues:
1. Check the troubleshooting section
2. Review application logs
3. Verify environment configuration
4. Test database connectivity
5. Check system resources

## 🆕 Deployment Notes (2024)

- **Auto-Migration:** The app now auto-migrates user table columns (full_name, last_login, etc.) on startup. Manual ALTER TABLE is not required for these fields.
- **Production-Ready:** All linter and runtime errors are fixed for smooth deployment.
- **Signup Bugfix:** Signup now works (get_user_by_username added to backend).
- **Analytics:** Watchlist and review analytics are available for each movie in both admin and user views.
- **Robust UI:** Profile images and sidebar clock are robust and production-ready.

## Streamlit Cloud Deployment Guide

## Prerequisites

1. **Database Setup**: Ensure your MySQL database is accessible from Streamlit Cloud
2. **Secrets Configuration**: Configure your `.streamlit/secrets.toml` file with database credentials
3. **Dependencies**: All required packages are listed in `requirements.txt`

## Deployment Steps

1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Connect to Streamlit Cloud**: 
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
3. **Configure Secrets**: Add your database credentials in the Streamlit Cloud dashboard

## Troubleshooting Common Issues

### ModuleNotFoundError: mysql.connector

**Solution**: The app now includes fallback database connectors:
- Primary: `mysql-connector-python==8.0.33`
- Fallback: `PyMySQL==1.1.0`

If you encounter this error:
1. Check that `requirements.txt` is in your repository root
2. Verify the MySQL connector version is compatible
3. The app will automatically fall back to PyMySQL if mysql.connector fails

### ModuleNotFoundError: sklearn

**Solution**: The app now includes fallback recommendation systems:
- Primary: `scikit-learn==1.3.0` with TF-IDF and cosine similarity
- Fallback: Simple genre-based recommendations

If you encounter this error:
1. Check that `requirements.txt` includes scikit-learn and its dependencies
2. The app will automatically use simple genre-based recommendations if scikit-learn fails
3. Both systems provide movie recommendations, but the fallback is less sophisticated

### Database Connection Issues

**Common Causes**:
- Database not accessible from Streamlit Cloud
- Incorrect credentials in secrets
- Database server blocking connections

**Solutions**:
1. Use a cloud database service (AWS RDS, Google Cloud SQL, etc.)
2. Ensure database allows connections from Streamlit Cloud IPs
3. Verify credentials in `.streamlit/secrets.toml`

### Testing Dependencies

Run these test scripts locally to verify functionality:
```bash
# Test database connection
python test_connection.py

# Test recommender system
python test_recommender.py
```

## Environment Variables

Make sure these are set in your Streamlit Cloud deployment:
- Database host, user, password, and database name
- Email configuration for notifications
- TMDB API key for movie data

## Performance Tips

1. **Database Connection Pooling**: The app uses connection pooling for better performance
2. **Caching**: Streamlit caching is implemented for expensive operations
3. **Pagination**: Large datasets are paginated to improve load times
4. **Fallback Systems**: Both database and recommender systems have fallbacks for reliability

## Security Considerations

1. **Database Credentials**: Never commit secrets to version control
2. **API Keys**: Store sensitive keys in Streamlit secrets
3. **User Authentication**: Implement proper user authentication and authorization

## Support

If you continue to experience issues:
1. Check the Streamlit Cloud logs for detailed error messages
2. Verify all dependencies are correctly specified
3. Test the database connection and recommender system locally first
4. The app includes fallback systems for both database and recommendation functionality

---

**🎬 Your Movie Recommendation System is now ready for production!** 