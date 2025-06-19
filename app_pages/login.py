import streamlit as st
import time
from utils.auth import login

def app():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        with st.spinner("Logging in..."):
            time.sleep(2)  # Simulate delay
            if username and password:
                login(username, password)
            else:
                st.error("Please enter both username and password")
    st.markdown('</div>', unsafe_allow_html=True)
