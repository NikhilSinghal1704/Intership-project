import streamlit as st
from utils.firebase_helper import get_applicants

def app():
    if not st.session_state.get("logged_in", False):
        st.error("🚫 Please log in.")
        st.stop()

    # Access URL query parameters
    query_params = st.query_params
    uid = query_params.get("aid", None)

    if not uid:
        st.info("UID not found in URL—please select an applicant from the list.")
        return

    data = get_applicants().get(uid)
    if not data:
        st.error(f"Applicant with ID {uid} not found.")
        return

    st.header(f"{data['name']} ({uid})")
    st.markdown(f"**Email:** {data['email']}  ")
    st.markdown(f"**Skills:** {', '.join(data.get('skills', []))}")
    st.markdown(f"**Experience:** {data.get('experience')} years")
    st.markdown(f"**Location:** {data.get('location')}")
    st.markdown(f"**Resume Path:** {data.get('resume_url','N/A')}")
