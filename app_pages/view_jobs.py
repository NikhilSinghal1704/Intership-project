import streamlit as st
from utils.firebase_helper import get_jobs

def app():
    st.title("📂 Available Jobs")
    jobs = get_jobs()
    if not jobs:
        st.info("No jobs posted yet.")
        return
    
    st.markdown("""
        <style>
        .job-card {
          border: 1px solid #ADD8E6;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 16px;
          transition: border 0.2s;
        }
        .job-card:hover {
          border: 2px solid #0D47A1;
        }
        .job-card a {
          text-decoration: none;
          color: inherit;
          display: block;
        }
        </style>
        """, unsafe_allow_html=True)


    st.markdown("""<!-- force HTML rendering -->""", unsafe_allow_html=True)

    for job_id, job in jobs.items():
        # Extract fields
        title = job.get("job_title", "Untitled")
        dept = job.get("department", "-")
        budget = job.get("budget", "-")
        posted_at = job.get("posted_at", "").split("T")[0] if job.get("posted_at") else "-"
        posted_by = job.get("posted_by", "-")

        # Build HTML card wrapped in link
        card_html = f"""
        <div class="job-card">
          <a href="/job_details?job_id={job_id}">
            <h3>{title}</h3>
            <p><b>Department:</b> {dept}</p>
            <p><b>Budget:</b> {budget}</p>
            <p><b>Posted on:</b> {posted_at}</p>
            <p><b>Posted by:</b> {posted_by}</p>
          </a>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
