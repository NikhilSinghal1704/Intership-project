import streamlit as st
from pages import add_applicant, view_applicants, add_job, add_application, dashboard, applicant_details

# Setup
st.set_page_config(page_title="Applicant Manager", layout="wide")

# Import necessary modules
import os
from utils.firebase_helper import init_firebase
from streamlit_cookies_manager import EncryptedCookieManager
from pages import login



@st.cache_resource
def initialize_firebase():
    return init_firebase()

def get_cookies():
    return EncryptedCookieManager(
        prefix="applicant-manager/",
        password=os.environ.get("COOKIES_PASSWORD", "default-cookie-pass")
    )

# Initialize DB and Cookies
if "db" not in st.session_state:
    st.session_state.db = initialize_firebase()

cookies = get_cookies()
if not cookies.ready():
    # Wait for cookie sync before rendering anything
    st.stop()

# Load login state from cookies
st.session_state.logged_in = cookies.get("logged_in") == "True"
st.session_state.username = cookies.get("username", None)

# Initialize other session keys
if "page" not in st.session_state:
    st.session_state.page = None
if "selected_applicant" not in st.session_state:
    st.session_state.selected_applicant = None



# 🛡 Login guard
if not st.session_state.logged_in:
    pages= {
        "Login": [
            st.Page(lambda: login.login_page(cookies), title="Login", icon="🔐", url_path="login")
        ]
    }
    st.sidebar.info("Please login to access tools.")

else:

    # Define pages grouped by section
    pages = {
        "Dashboard": [
            st.Page(dashboard.app, title="Dashboard", icon="📊", url_path="dashboard", default=True)
        ],
        "Applicant Tools": [
            st.Page(add_applicant.app, title="Add Applicant", icon="➕", url_path="add_applicant"),
            st.Page(view_applicants.app, title="View Applicants", icon="👁️", url_path="view_applicants"),
            st.Page(applicant_details.app, title="Applicant Details", icon="📄", url_path="applicant_detail")
        ],
        "Job Management": [
            st.Page(add_job.app, title="Add Job Opening", icon="💼", url_path="add_job"),
        ],
        "Applications": [
            st.Page(add_application.app, title="Add Application", icon="📁", url_path="add_application"),
        ],
        "Account": [
            st.Page(lambda: login.logout_page(cookies), title="Logout", icon="🚪", url_path="logout"),
        ],
    }


current_page = st.navigation(pages, position="sidebar")
current_page.run()

