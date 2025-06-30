import streamlit as st
from utils.firebase_helper import get_jobs, get_applications_for_jobs, get_applicants
from datetime import datetime
import plotly.express as px
import pandas as pd

def app():
    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in.")
        st.stop()

    params = st.query_params
    job_id = params.get("job_id", None)
    if not job_id:
        st.info("Select a job first.")
        return

    job = get_jobs([job_id]).get(job_id)
    if not job:
        st.error("Job not found.")
        return
    
    tabs = st.tabs(["Details", "Applications"])

    with tabs[0]:

        # -- Header --
        st.title(f"💼 {job.get('job_title', '-')}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Department:** {job.get('department', '-')}")
            st.write(f"**Location:** {job.get('location', '-')}")
            st.write(f"**Work Mode:** {job.get('work_mode', '-')}")
            st.write(f"**Duration:** {job.get('job_duration', '-')}")
        with col2:
            st.write(f"**Budget:** {job.get('budget', '-')}")
            st.write(f"**Vacancies:** {job.get('vacancies', '-')}")
            st.write(f"**Experience Required:** {job.get('experience_required', '-')}")
            posted = job.get('posted_at')
            if posted:
                posted = datetime.fromisoformat(posted).strftime("%Y-%m-%d")
            st.write(f"**Posted on:** {posted}")
            st.write(f"**Posted by:** {job.get('posted_by', '-')}")

        st.markdown("---")

        # -- Details Sections --
        st.subheader("📄 Description")
        st.write(job.get("description", "-"))

        st.subheader("📝 Responsibilities")
        st.write(job.get("responsibilities", "-"))

        st.subheader("🎯 Qualifications")
        st.write(job.get("qualifications", "-"))

        st.subheader("🎁 Benefits")
        st.write(job.get("benefits", "-"))

        st.subheader("🛠️ Required Skills")
        skills = job.get("skills", [])
        if skills:
            st.write(", ".join(skills))
        else:
            st.write("-")

        st.subheader("🧭 Hiring Stages")
        stages = job.get("hiring_process", [])
        if stages:
            st.write(" → ".join(stages))
        else:
            st.write("-")

        st.markdown("---")

        # -- Download or Manage Button --
        st.download_button(label="📥 Export Job Data as JSON", data=str(job), file_name=f"{job_id}.json")

    with tabs[1]:
        st.subheader("📊 Applications Overview")
        apps = get_applications_for_jobs(job_id)
        if not apps:
            st.info("No applications yet.")
            return

        # Build DataFrame
        rows = []
        applicant_ids = [app["applicant_id"] for app in apps.values()]
        applicants = get_applicants(applicant_ids)

        for app_id, app_data in apps.items():
            aid = app_data["applicant_id"]
            person = applicants.get(aid, {})
            rows.append({
                "Applicant ID": f'<a href="/applicant_detail?uid={aid}">{aid}</a>',
                "Name": person.get("name", "-"),
                "Email": person.get("email", "-"),
                "Status": app_data.get("status", "-"),
                "Applied On": app_data.get("applied_at", "").split("T")[0],
            })

        df = pd.DataFrame(rows)

        # Sidebar filters
        st.sidebar.subheader("🔍 Filter Applications")
        status_opts = ["All"] + sorted(df["Status"].unique().tolist())
        chosen_status = st.sidebar.selectbox("Application Status", status_opts)
        name_search = st.sidebar.text_input("Search by Name or Email")

        if chosen_status != "All":
            df = df[df["Status"] == chosen_status]
        if name_search:
            df = df[df["Name"].str.contains(name_search, case=False) |
                    df["Email"].str.contains(name_search, case=False)]

        # Display as HTML table to preserve links
        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("---")

        if apps:
            # Count statuses
            statuses = [app.get("status", "applied") for app in apps.values()]
            df = pd.Series(statuses).value_counts().reset_index()
            df.columns = ["Stage", "Count"]
        
            fig_pie = px.pie(
                df,
                names="Stage",
                values="Count",
                title="Applicants by Stage",
                hole=0.3,  # donut-shaped
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)   
