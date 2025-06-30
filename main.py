import streamlit as st
from app_pages import view_applicants, add_job, add_application, dashboard, applicant_details, login, logout, add_user, view_jobs, job_details, add_applicant

# Setup
st.set_page_config(page_title="Applicant Manager", layout="wide")

# Import necessary modules
from utils.firebase_helper import init_firebase
from utils.auth import auto_login, initialize_session



# Initialize Firebase connection
def initialize_firebase():
    return init_firebase()

# Initialize DB and Cookies
if "db" not in st.session_state:
    st.session_state.db = initialize_firebase()

st.session_state.logged_in = False
st.session_state.username = None
initialize_session()
auto_login()


# 🛡 Login guard
if not st.session_state.logged_in:
    pages= {
        "Login": [
            st.Page(login.app, title="Login", icon="🔐", url_path="login")
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
            st.Page(view_jobs.app, title="Available Jobs", icon="💼", url_path="view_jobs"),
            st.Page(job_details.app, title="Job Details", icon="📄", url_path="job_details"),
        ],
        "Applications": [
            st.Page(add_application.app, title="Add Application", icon="📁", url_path="add_application"),
        ],
        "Account": [
            st.Page(logout.app, title="Logout", icon="🚪", url_path="logout"),
        ],
    }

if st.session_state.get("username") == "admin":
    pages["Account"].append(st.Page(add_user.app, title="Add User", icon="🛠️", url_path="add_user"))


current_page = st.navigation(pages, position="sidebar")
current_page.run()