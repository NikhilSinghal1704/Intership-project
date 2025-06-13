import streamlit as st
from utils.firebase_helper import get_open_jobs, get_applicants, add_application

def app():
    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in.")
        st.stop()

    st.title("📝 Add Job Application")

    jobs = get_open_jobs()
    if not jobs:
        st.warning("No open jobs found.")
        return

    job_options = {f"{v['job_title']} ({k})": k for k, v in jobs.items()}
    applicants = get_applicants()
    if not applicants:
        st.warning("No applicants found.")
        return

    applicant_options = {f"{v['name']} ({k})": k for k, v in applicants.items()}

    with st.form("application_form"):
        job_sel = st.selectbox("Select Job", list(job_options.keys()))
        app_sel = st.selectbox("Select Applicant", list(applicant_options.keys()))

        submitted = st.form_submit_button("Submit Application")

        if submitted:
            job_id = job_options[job_sel]
            applicant_id = applicant_options[app_sel]
            add_application(job_id, applicant_id)
            st.success("✅ Application linked!")
