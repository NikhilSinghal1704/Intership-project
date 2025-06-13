import streamlit as st
from utils.firebase_helper import get_applicants

def app():
    
    # Retrieve UUID from session_state or localStorage
    uid = st.session_state.get("selected_applicant") or st.experimental_get_query_params().get("uid", [None])[0]

    if not uid:
        st.info("Select an applicant from the View page.")
        return

    st.session_state.selected_applicant = uid

    data = get_applicants().get(uid)
    if not data:
        st.error("Applicant not found.")
        return

    st.header(f"{data.get('name')} ({uid})")
    st.markdown(f"**Email:** {data.get('email')}")
    st.markdown(f"**Skills:** {', '.join(data.get('skills', []))}")
    st.markdown(f"**Experience:** {data.get('experience')} years")
    st.markdown(f"**Location:** {data.get('location')}")
    st.markdown(f"**Resume Path:** {data.get('resume_url', 'N/A')}")
