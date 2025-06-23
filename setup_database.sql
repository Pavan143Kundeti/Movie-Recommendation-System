-- Create the database
CREATE DATABASE IF NOT EXISTS movie_db;
USE movie_db;

-- The tables will be created automatically by the Streamlit app
-- This script just ensures the database exists

-- Optional: Create a test admin user (you can modify the credentials)
-- INSERT INTO users (username, email, password_hash, role) VALUES 
-- ('admin', 'admin@example.com', SHA2('admin123', 256), 'admin'); 