#!/usr/bin/env python3
"""
Script to create admin user
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simulate Streamlit secrets
class MockSecrets:
    def __init__(self):
        self.mysql = {
            'host': 'sql12.freesqldatabase.com',
            'user': 'sql12786417',
            'password': 'm46Km6gKDb',
            'database': 'sql12786417'
        }
    
    def __getitem__(self, key):
        return getattr(self, key)

# Mock streamlit
import streamlit as st
st.secrets = MockSecrets()

print("🔧 Creating admin user...")

try:
    from modules.database import get_conn, get_cursor, hash_password, add_user
    
    # Check if admin user already exists
    conn = get_conn()
    cursor = get_cursor(conn)
    
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_user = cursor.fetchone()
    
    if admin_user:
        print("✅ Admin user already exists!")
        print(f"   Username: {admin_user['username']}")
        print(f"   Email: {admin_user.get('email', 'N/A')}")
        print(f"   Role: {admin_user.get('role', 'N/A')}")
    else:
        print("📝 Creating new admin user...")
        
        # Create admin user
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_password = "admin12"
        admin_password_hash = hash_password(admin_password)
        
        # Insert admin user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name, is_verified) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (admin_username, admin_email, admin_password_hash, 'admin', 'Administrator', True))
        
        conn.commit()
        print("✅ Admin user created successfully!")
        print(f"   Username: {admin_username}")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   Role: admin")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error creating admin user: {e}")
    import traceback
    traceback.print_exc()

print("🏁 Admin user setup completed.") 