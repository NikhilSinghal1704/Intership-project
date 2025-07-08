import streamlit as st
import pandas as pd
from utils.firebase_helper import get_jobs, get_applications_for_jobs
from datetime import datetime, timedelta

def build_dataframe(jobs):
    rows = []
    for job_id, job in jobs.items():
        applications = get_applications_for_jobs(job_id)
        applicant_count = len(applications) if applications else 0

        posted_at = job.get("posted_at", "")
        posted_on = posted_at.split("T")[0] if posted_at else "-"

        rows.append({
            "ID": job_id,
            "Title": job.get("job_title", "-"),
            "Location": job.get("location", "-"),
            "Work Mode": job.get("work_mode", "-"),
            "Vacancies": job.get("vacancies", "-"),
            "Applicants": applicant_count,
            "Status": job.get("status", "open").capitalize(),
            "Posted On": posted_on,
            "Details": f"/job_details?job_id={job_id}"
        })

    df = pd.DataFrame(rows)
    df["Posted On"] = pd.to_datetime(df["Posted On"], errors="coerce")

    return df

def app():

    # 🛑 Login guard
    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in.")
        st.stop()

    with st.spinner("Loading job postings..."):
        jobs = get_jobs()

    if not jobs:
        st.info("No job postings found.")
        return

    with st.spinner("Building job data..."):
        df = build_dataframe(jobs)

    # -------------------- FILTERS --------------------
    with st.sidebar:
        st.header("🔎 Filter Jobs")

        title_search = st.text_input("Search by Title")

        location_filter = st.selectbox(
            "📍 Location",
            options=["All"] + sorted(df["Location"].dropna().unique().tolist())
        )

        mode_filter = st.selectbox(
            "💼 Work Mode",
            options=["All"] + sorted(df["Work Mode"].dropna().unique().tolist())
        )

        status_filter = st.selectbox(
            "📌 Status",
            options=["All"] + sorted(df["Status"].dropna().unique().tolist())
        )

        date_filter = st.selectbox(
            "🗓️ Posted Date",
            options=["All Time", "Today", "This Week", "This Month", "This Year"]
        )

    # -------------------- APPLY FILTERS --------------------
    mask = pd.Series(True, index=df.index)
    
    if title_search:
        mask &= df["Title"].str.contains(title_search, case=False, na=False)
    
    if location_filter != "All":
        mask &= df["Location"] == location_filter
    
    if mode_filter != "All":
        mask &= df["Work Mode"] == mode_filter
    
    if status_filter != "All":
        mask &= df["Status"] == status_filter
    
    df = df.loc[mask]

    now = datetime.now()
    if date_filter != "All Time":
        if date_filter == "Today":
            start_date = now.date()
        elif date_filter == "This Week":
            start_date = (now - timedelta(days=now.weekday())).date()
        elif date_filter == "This Month":
            start_date = now.replace(day=1).date()
        elif date_filter == "This Year":
            start_date = now.replace(month=1, day=1).date()

        df = df[df["Posted On"].dt.date >= start_date]

    # Reformat date for display
    df["Posted On"] = df["Posted On"].dt.strftime("%Y-%m-%d")
    
    # -------------------- DISPLAY --------------------
    n_rows = len(df)
    height = min((n_rows + 1) * 35 + 5, 800)  # Cap at e.g. 800px to avoid massive pages

    st.header(f"📄 Job Listings ({n_rows})")
    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True,
        column_config={
            "Details": st.column_config.LinkColumn(
                label="Details",
                help="Click to view applicant details",
                display_text="View"
            )
        },
    )
