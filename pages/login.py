import streamlit as st

USERS = {
    "admin": "admin123",
    "hr": "hr2024"
}

def login_page(cookies):
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if USERS.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            cookies["logged_in"] = "True"
            cookies["username"] = username
            cookies.save()
            st.success("✅ Logged in successfully!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

def logout_page(cookies):
    st.title("🚪 Logout")
    st.session_state.logged_in = False
    st.session_state.username = None
    cookies["logged_in"] = ""
    cookies["username"] = ""
    cookies.save()
    st.success("✅ Logged out successfully!")
    st.rerun()
