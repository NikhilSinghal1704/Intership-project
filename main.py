import streamlit as st
from utils.firebase_helper import init_firebase
from pages import login

# Firebase client
@st.cache_resource
def initialize_firebase():
    return init_firebase()

if "db" not in st.session_state:
    st.session_state.db = initialize_firebase()

# Initialize login state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Navigation Sidebar
st.sidebar.title("📋 Navigation")

if not st.session_state.logged_in:
    with st.sidebar:
        st.subheader("🔐 Login")
        st.info("Please login to access tools.")
    login.login_page()
    st.stop()

with st.sidebar:
    st.subheader("👤 Applicant Tools")
    if st.button("Add Applicant"):
        st.session_state.page = "add_applicant"

    st.subheader("💼 Job Management")
    if st.button("Add Job Opening"):
        st.session_state.page = "add_job"

    st.subheader("📁 Applications")
    if st.button("Add Application"):
        st.session_state.page = "add_application"

    st.subheader("🚪 Logout")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

# Page routing
page = st.session_state.get("page", None)

if page == "add_applicant":
    __import__("pages.add_applicant", fromlist=["app"]).app()
elif page == "add_job":
    __import__("pages.add_job", fromlist=["app"]).app()
elif page == "add_application":
    __import__("pages.add_application", fromlist=["app"]).app()
else:
    st.title("Welcome!")
    st.markdown(f"👋 Hello, **{st.session_state.username}**. Use the sidebar to navigate.")
