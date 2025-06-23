import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_otp_email(recipient_email, otp_code, purpose='signup'):
    """Sends an OTP email using credentials from st.secrets."""
    
    # --- Validate secrets exist ---
    if "email" not in st.secrets or not all(k in st.secrets["email"] for k in ["sender_email", "sender_password"]):
        st.error("Email configuration is missing from secrets.toml. Cannot send OTP.")
        return False

    sender_email = st.secrets["email"]["sender_email"]
    sender_password = st.secrets["email"]["sender_password"]
    smtp_server = st.secrets["email"].get("smtp_server", "smtp.gmail.com")
    smtp_port = st.secrets["email"].get("smtp_port", 587)

    # --- Create the email message ---
    if purpose == 'signup':
        subject = "Verify Your Account - Movie Recommender"
        body = f"""
        <html>
        <body>
            <h2>Welcome to the Movie Recommendation System!</h2>
            <p>Thank you for signing up. Please use the following One-Time Password (OTP) to verify your email address:</p>
            <h3 style="color: #007BFF; font-size: 24px; text-align: center;">{otp_code}</h3>
            <p>This OTP is valid for 5 minutes. If you did not request this, please ignore this email.</p>
            <hr>
            <p style="font-size: 0.9em; color: #6c757d;">This is an automated message. Please do not reply.</p>
        </body>
        </html>
        """
    elif purpose == 'reset':
        subject = "Your Password Reset Code - Movie Recommender"
        body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>We received a request to reset the password for your account. Use the code below to complete the reset process:</p>
            <h3 style="color: #007BFF; font-size: 24px; text-align: center;">{otp_code}</h3>
            <p>This code is valid for 5 minutes. If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
            <hr>
            <p style="font-size: 0.9em; color: #6c757d;">This is an automated message. Please do not reply.</p>
        </body>
        </html>
        """
    else:
        return False # Invalid purpose

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    # Attach the HTML body
    message.attach(MIMEText(body, "html"))

    # --- Send the email ---
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        return True
    except smtplib.SMTPAuthenticationError:
        st.error("Failed to authenticate with the email server. Please check your sender_email and sender_password in secrets.toml.")
        return False
    except Exception as e:
        st.error(f"An error occurred while sending the email: {e}")
        return False 