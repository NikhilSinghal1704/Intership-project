import streamlit as st
from utils.auth import save_user, load_users, hash_password

def app():
    # 🛑 Login guard
    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in.")
        st.stop()
    
    st.title("➕ Add User")
    st.write("Enter a new username and password to register a new user.")

    with st.form("add_user_form"):
        new_username = st.text_input("Username").strip()
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Add User")

    if submit:
        # 🛑 Check all fields filled
        if not new_username or not new_password or not confirm_password:
            st.warning("All fields are required.")
            return
        
        # 🛑 Check passwords match
        if new_password != confirm_password:
            st.error("❌ Passwords do not match. Please try again.")
            return
        
        users = load_users()
        if new_username in users:
            st.error("⚠️ Username already exists. Try another.")
            return
        
        # ✅ Hash and save
        pw_hash = hash_password(new_password)
        save_user(new_username, pw_hash)
        st.success(f"✅ User `{new_username}` added successfully!")
