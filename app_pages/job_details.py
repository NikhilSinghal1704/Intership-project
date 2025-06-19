import streamlit as st
from utils.firebase_helper import get_jobs

def app():
    params = st.query_params
    job_id = params.get("job_id", None)
    if not job_id:
        st.info("Select a job first.")
        return

    job = get_jobs([job_id]).get(job_id)
    if not job:
        st.error("Job not found.")
        return

    st.header(job["job_title"])
    st.write(f"**Department:** {job['department']}")
    st.write(f"**Budget:** {job['budget']}")
    st.write(f"**Experience required:** {job['experience_required']}")
    st.write(f"**Posted on:** {job['posted_at'].split('T')[0]}")
    st.write(f"**Posted by:** {job['posted_by']}")
    st.markdown("---")
    st.subheader("Description")
    st.write(job.get("description", ""))
