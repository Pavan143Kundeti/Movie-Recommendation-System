import streamlit as st
from modules import database
from modules.email_utils import send_otp_email
from modules.localization import get_text
import time

def signup_page():
    """Page for new user registration and OTP verification."""

    st.title(get_text("signup_title") or "📝 Create Your Account")

    # --- Initialize session state variables ---
    if 'signup_step' not in st.session_state:
        st.session_state.signup_step = "form" # Can be "form", "verify_otp", "verified"
    if 'signup_email' not in st.session_state:
        st.session_state.signup_email = None
    if 'signup_username' not in st.session_state:
        st.session_state.signup_username = None
    if 'otp_resent' not in st.session_state:
        st.session_state.otp_resent = False
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False

    # --- Step 1: Show Signup Form ---
    if st.session_state.signup_step == "form":
        st.header("📝 Create New Account")
        with st.form(key="signup_form", clear_on_submit=False):
            st.info("Your email will be verified on this page before you can log in.")
            
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username*")
                password = st.text_input("Password*", type="password")
            with col2:
                email = st.text_input("Email*")
                confirm_password = st.text_input("Confirm Password*", type="password")
            
            phone_number = st.text_input("Phone Number (Optional)")

            submit_button = st.form_submit_button("Create Account & Send OTP")

            if submit_button:
                if not all([username, email, password, confirm_password]):
                    st.warning("Please fill out all required fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif database.get_user_by_username(username) or database.get_user_by_email(email):
                    st.error("Username or email already exists. Please try logging in.")
                else:
                    with st.spinner("Creating account and sending OTP..."):
                        user_id = database.add_user(username, email, password, phone_number)
                        if user_id:
                            otp_code = database.generate_otp()
                            database.store_otp(email, otp_code, 'signup')
                            if send_otp_email(email, otp_code, 'signup'):
                                # Transition to OTP verification step
                                st.session_state.signup_step = "verify_otp"
                                st.session_state.signup_email = email
                                st.session_state.signup_username = username
                                st.rerun()
                            else:
                                st.error("Failed to send OTP. Please check your email address.")
    
    # --- Step 2: Show OTP Verification Form ---
    elif st.session_state.signup_step == "verify_otp":
        st.header(f"🔐 Verify Your Email: {st.session_state.signup_email}")
        st.info("An OTP has been sent to your email. Please enter it below.")
        
        with st.form(key="otp_form"):
            otp_code = st.text_input("Enter OTP Code")
            verify_button = st.form_submit_button("Verify Account")

            if verify_button:
                if database.validate_otp(st.session_state.signup_email, otp_code, 'signup'):
                    database.set_user_verified(st.session_state.signup_email)
                    st.session_state.signup_step = "verified"
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Invalid or expired OTP. Please try again.")

        if st.button("Resend OTP"):
            with st.spinner("Resending OTP..."):
                if database.resend_otp(st.session_state.signup_email, 'signup'):
                    st.toast("A new OTP has been sent!", icon="✉️")
                else:
                    st.error("Failed to resend OTP. Please wait a moment before trying again.")
    
    # --- Step 3: Show Success and Login Button ---
    elif st.session_state.signup_step == "verified":
        st.header("✅ Verification Successful!")
        st.success(f"Thank you for verifying, **{st.session_state.signup_username}**! Your account is now active.")
        
        st.info("You can now log in to access the platform.")
        
        if st.button("Proceed to Login", type="primary"):
            # Clean up signup state and switch to login view
            for key in ['signup_step', 'signup_email', 'signup_username', 'otp_resent']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Since we can't directly log in from another page,
            # we guide the user back to the main login.
            st.switch_page("app.py")

def main():
    """Main function to display the signup page."""
    signup_page()

if __name__ == "__main__":
    st.set_page_config(layout="centered", page_title="Sign Up")
    main() 