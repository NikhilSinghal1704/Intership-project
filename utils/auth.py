import streamlit as st
import bcrypt, os, json
from datetime import datetime
from streamlit_cookies_manager import EncryptedCookieManager


cookies = EncryptedCookieManager(
    prefix="nikhil/streamlit-cookies-manager/",
    password=os.environ.get("COOKIES_PASSWORD", "default-cookie-pass"),
)
if not cookies.ready():
    st.error("Cookies are not ready. Please refresh the page.")
    st.spinner()
    st.stop()

# Function to hash a password using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

# Function to load users from a JSON file
def load_users():
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
        return users
    except FileNotFoundError:
        return {}

# Function to save a new user to the JSON file
def save_user(username, password_hash):
    users = load_users()
    users[username] = password_hash.decode("utf-8")
    with open("users.json", "w") as f:
        json.dump(users, f)

# Function to manage login
def login(username, password):
    users = load_users()
    if username in users and check_password(bytes(users[username], "utf-8"), password):
        st.session_state.username = username
        cookies["username"] = username  # Store username in cookie
        cookies.save()  # Save cookie
        st.success(f"Logged in as {username}")
        st.session_state.logged_in = True
        st.session_state.last_activity_time = datetime.now()
        st.rerun()  # Use st.rerun() here instead of st.experimental_rerun()
    else:
        st.error("Invalid username or password!")

def auto_login():
    """
    Check if a username exists in the cookies and update session state accordingly.
    """
    username = cookies.get("username", None)
    if username:
        st.session_state.username = username
        st.session_state.logged_in = True

def initialize_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'last_activity_time' not in st.session_state:
        st.session_state.last_activity_time = datetime.now()

def logout():
    # Ensure cookies are ready
    if not cookies.ready():
        st.stop()
    # Clear cookie and update session state
    cookies["username"] = ""
    cookies.save()
    st.session_state.username = None
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.rerun()

if __name__ == "__main__":
    print("Add a User")
    username = input("Enter username: ")
    password = input("Enter password: ")
    confirm_password = input("Confirm password: ")
    if password == confirm_password:
        hashed_password = hash_password(password)
        save_user(username, hashed_password)
        print(f"User {username} has been created successfully!")
    else:
        print("Passwords do not match.")