import streamlit as st
import time
from utils.auth import logout, initialize_session


def app():
    # Initialize session state for login tracking.
    initialize_session()

    st.title("Logout")
    st.write("Click the button below to log out.")

    if st.button("Logout"):
        with st.spinner("Logging out..."):
            time.sleep(1)  # Simulate a delay (if needed)
            logout()
