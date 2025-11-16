import streamlit as st
import os
import re
import json
import hashlib
import time
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId


from urllib.parse import quote_plus

def get_db_connection():
    """Connect to MongoDB and return the database connection"""
    username = quote_plus("abinaya93004")
    password = quote_plus("Abinaya@123")
    cluster = "cluster0.rlfliqb.mongodb.net"
    db_name = "AI-Hiring"

    MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName=Cluster0"

    client = MongoClient(MONGO_URI)
    db = client[db_name]
    return db

# Function to hash passwords securely
def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest()
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt.encode('ascii'), 100000)
    pwdhash = pwdhash.hex()
    return salt + pwdhash


# Function to verify hashed passwords
def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_hash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = pwdhash.hex()
    return pwdhash == stored_hash


# Function to validate email format
def is_valid_email(email):
    """Check if email format is valid"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


# Function to validate password strength
def is_strong_password(password):
    """Check if password meets strength requirements"""
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"


# Function to load user data
def load_user_by_email(email):
    """Load a user by email from MongoDB"""
    db = get_db_connection()
    user_collection = db['User_credentials']
    user = user_collection.find_one({"email": email.lower()})
    return user

def load_user_by_id(user_id):
    """Load a user by ID from MongoDB"""
    db = get_db_connection()
    user_collection = db['User_credentials']
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    return user

# Function to create a new user
def create_user(email, password, name, company=None):
    """Create a new user and save to MongoDB"""
    db = get_db_connection()
    user_collection = db['User_credentials']

    # Check if email already exists
    if user_collection.find_one({"email": email.lower()}):
        return False, "Email already registered"

    # Create new user document
    user = {
        "email": email.lower(),
        "password": hash_password(password),
        "name": name,
        "company": company,
        "created_at": datetime.now(),
        "last_login": None
    }

    # Insert into database
    result = user_collection.insert_one(user)

    if result.inserted_id:
        return True, "User created successfully"
    else:
        return False, "Failed to create user"


# Function to authenticate user
def authenticate(email, password):
    """Authenticate a user with email and password"""
    user = load_user_by_email(email.lower())

    if not user:
        return False, "Email not found", None

    if not verify_password(user["password"], password):
        return False, "Incorrect password", None

    # Update last login time
    db = get_db_connection()
    user_collection = db['User_credentials']
    user_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.now()}}
    )

    return True, "Login successful", user


# Load custom CSS styling
def load_auth_css():
    st.markdown(
        """
        <style>
        .main {
            background-color: transparent !important;
            padding: 20px;
            border-radius: 10px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .auth-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .auth-header {
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }
        .auth-logo {
            width: 50px;
            height: 50px;
            background-color: #1c6758;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 20px;
            margin-right: 15px;
        }
        .auth-title {
            font-size: 28px;
            font-weight: bold;
            color: #1c6758;
        }
        .auth-subtitle {
            font-size: 16px;
            color: #666;
            margin-top: 5px;
        }
        .auth-form {
            margin-top: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-label {
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }
        .stButton > button {
            border-radius: 30px;
            background-color: #1c6758;
            color: white;
            border: none;
            padding: 10px 24px;
            font-weight: bold;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #134e4a;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .auth-footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }
        .auth-switch {
            text-align: center;
            margin-top: 20px;
            color: #666;
        }
        .auth-switch a {
            color: #1c6758;
            text-decoration: none;
            font-weight: bold;
        }
        .auth-switch a:hover {
            text-decoration: underline;
        }
        .success-message {
            padding: 10px;
            background-color: rgba(46, 204, 113, 0.2);
            border-left: 4px solid #2ecc71;
            color: #27ae60;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .error-message {
            padding: 10px;
            background-color: rgba(231, 76, 60, 0.2);
            border-left: 4px solid #e74c3c;
            color: #c0392b;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .info-message {
            padding: 10px;
            background-color: rgba(52, 152, 219, 0.2);
            border-left: 4px solid #3498db;
            color: #2980b9;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .forgot-password {
            text-align: right;
            margin-top: -15px;
            margin-bottom: 20px;
        }
        .forgot-password a {
            color: #1c6758;
            text-decoration: none;
            font-size: 14px;
        }
        .forgot-password a:hover {
            text-decoration: underline;
        }
        .password-requirements {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .stTextInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.1);
            color: black;
            border-radius: 30px;
            border: 1px solid #ddd;
            font-size: 16px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            padding: 10px 15px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Function to show login page
def show_login_page():
    # Header with logo and title
    st.markdown(
        """
        <div class='auth-header'>
            <div class='auth-logo'>HS</div>
            <div>
                <div class='auth-title'>HireSense AI</div>
                <div class='auth-subtitle'>Smart Recruitment Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display any messages
    if "auth_message" in st.session_state and "auth_message_type" in st.session_state:
        message_type = st.session_state.auth_message_type
        message = st.session_state.auth_message
        st.markdown(f"<div class='{message_type}-message'>{message}</div>", unsafe_allow_html=True)
        # Clear message after displaying
        del st.session_state.auth_message
        del st.session_state.auth_message_type

    # Login form
    with st.form(key="login_form"):
        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        st.markdown("<div class='form-label'>Email</div>", unsafe_allow_html=True)
        email = st.text_input("", key="login_email", placeholder="Enter your email")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        st.markdown("<div class='form-label'>Password</div>", unsafe_allow_html=True)
        password = st.text_input("", key="login_password", placeholder="Enter your password", type="password")
        st.markdown("</div>", unsafe_allow_html=True)

        # Forgot password link
        st.markdown("<div class='forgot-password'><a href='#'>Forgot password?</a></div>", unsafe_allow_html=True)

        submit_button = st.form_submit_button(label="Sign In")

        if submit_button:
            if not email or not password:
                st.session_state.auth_message = "Please fill in all fields"
                st.session_state.auth_message_type = "error"
                st.rerun()

            # Attempt login
            success, message, user_data = authenticate(email, password)

            if success:
                st.session_state.auth_message = "Login successful! Redirecting..."
                st.session_state.auth_message_type = "success"

                # Set session as authenticated
                st.session_state.authenticated = True
                st.session_state.user_email = email.lower()

                # Set user info from MongoDB user data
                st.session_state.user_name = user_data["name"]
                st.session_state.user_company = user_data.get("company", "")

                # Add a short delay to show success message
                time.sleep(1)
                st.rerun()
            else:
                st.session_state.auth_message = message
                st.session_state.auth_message_type = "error"
                st.rerun()

    # Switch to signup
    st.markdown(
        """
        <div class='auth-switch'>
            Don't have an account?
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Sign up instead", key="switch_to_signup"):
        st.session_state.auth_page = "signup"
        st.rerun()

    # Footer
    st.markdown(
        """
        <div class='auth-footer'>
            © 2025 HireSense AI - Smart Recruitment Assistant
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# Function to show signup page
def show_signup_page():
    # Header with logo and title
    st.markdown(
        """
        <div class='auth-header'>
            <div class='auth-logo'>HS</div>
            <div>
                <div class='auth-title'>Create an Account</div>
                <div class='auth-subtitle'>Join HireSense AI Recruitment Platform</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display any messages
    if "auth_message" in st.session_state and "auth_message_type" in st.session_state:
        message_type = st.session_state.auth_message_type
        message = st.session_state.auth_message
        st.markdown(f"<div class='{message_type}-message'>{message}</div>", unsafe_allow_html=True)
        # Clear message after displaying
        del st.session_state.auth_message
        del st.session_state.auth_message_type

    # Signup form
    with st.form(key="signup_form"):
        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        st.markdown("<div class='form-label'>Full Name</div>", unsafe_allow_html=True)
        name = st.text_input("", key="signup_name", placeholder="Enter your full name")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        st.markdown("<div class='form-label'>Email</div>", unsafe_allow_html=True)
        email = st.text_input("", key="signup_email", placeholder="Enter your email")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        st.markdown("<div class='form-label'>Password</div>", unsafe_allow_html=True)
        password = st.text_input("", key="signup_password", placeholder="Create a password", type="password")
        st.markdown(
            "<div class='password-requirements'>Password must be at least 8 characters with uppercase, lowercase, and numbers</div>",
            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        st.markdown("<div class='form-label'>Confirm Password</div>", unsafe_allow_html=True)
        confirm_password = st.text_input("", key="signup_confirm", placeholder="Confirm your password", type="password")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
        st.markdown("<div class='form-label'>Company (Optional)</div>", unsafe_allow_html=True)
        company = st.text_input("", key="signup_company", placeholder="Enter your company name (optional)")
        st.markdown("</div>", unsafe_allow_html=True)

        submit_button = st.form_submit_button(label="Sign Up")

        if submit_button:
            if not name or not email or not password or not confirm_password:
                st.session_state.auth_message = "Please fill in all required fields"
                st.session_state.auth_message_type = "error"
                st.rerun()

            # Validate email format
            if not is_valid_email(email):
                st.session_state.auth_message = "Please enter a valid email address"
                st.session_state.auth_message_type = "error"
                st.rerun()

            # Validate password strength
            is_strong, pwd_message = is_strong_password(password)
            if not is_strong:
                st.session_state.auth_message = pwd_message
                st.session_state.auth_message_type = "error"
                st.rerun()

            # Confirm passwords match
            if password != confirm_password:
                st.session_state.auth_message = "Passwords do not match"
                st.session_state.auth_message_type = "error"
                st.rerun()

            # Attempt to create user
            success, message = create_user(email, password, name, company)

            if success:
                st.session_state.auth_message = "Account created successfully! Please log in."
                st.session_state.auth_message_type = "success"
                st.session_state.auth_page = "login"
                st.rerun()
            else:
                st.session_state.auth_message = message
                st.session_state.auth_message_type = "error"
                st.rerun()

        # Switch to login
    st.markdown(
        """
        <div class='auth-switch'>
            Already have an account?
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Sign in instead", key="switch_to_login"):
        st.session_state.auth_page = "login"
        st.rerun()

    # Footer
    st.markdown(
        """
        <div class='auth-footer'>
            © 2025 HireSense AI - Smart Recruitment Assistant
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# Function to show authentication flow and manage session state
def auth_flow():
    # Initialize session state variables if they don't exist
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Load custom CSS
    load_auth_css()

    # Show appropriate page based on session state
    if not st.session_state.authenticated:
        if st.session_state.auth_page == "login":
            show_login_page()
        elif st.session_state.auth_page == "signup":
            show_signup_page()

    return st.session_state.authenticated


# Main function to run this as a standalone app
if __name__ == "__main__":
    auth_flow()