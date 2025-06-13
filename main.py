import streamlit as st
from utils.firebase_helper import init_firebase
from pages import login

# Set app-wide config once
st.set_page_config(page_title="Applicant Manager", layout="wide")

@st.cache_resource
def initialize_firebase():
    return init_firebase()

if "db" not in st.session_state:
    st.session_state.db = initialize_firebase()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "selected_applicant" not in st.session_state:
    st.session_state.selected_applicant = None
if "page" not in st.session_state:
    st.session_state.page = None

# Login guard
if not st.session_state.logged_in:
    st.sidebar.subheader("🔐 Login")
    st.sidebar.info("Please login to access tools.")
    login.login_page()
    st.stop()

# Sidebar navigation
st.sidebar.title("📋 Navigation")

with st.sidebar:
    st.subheader("👤 Applicant Tools")
    if st.button("Add Applicant"):
        st.session_state.page = "add_applicant"
    if st.button("View Applicants"):
        st.session_state.page = "view_applicants"

    st.subheader("💼 Job Management")
    if st.button("Add Job Opening"):
        st.session_state.page = "add_job"

    st.subheader("📁 Applications")
    if st.button("Add Application"):
        st.session_state.page = "add_application"

    st.subheader("🚪 Logout")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# Default landing
if st.session_state.page is None:
    st.session_state.page = "view_applicants"

# Page routing
page = st.session_state.page

if page == "add_applicant":
    __import__("pages.add_applicant", fromlist=["app"]).app()
elif page == "view_applicants":
    __import__("pages.view_applicants", fromlist=["app"]).app()
elif page == "add_job":
    __import__("pages.add_job", fromlist=["app"]).app()
elif page == "add_application":
    __import__("pages.add_application", fromlist=["app"]).app()
else:
    st.error("Error: Unknown page: " + str(page))
