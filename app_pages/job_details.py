import streamlit as st
from utils.firebase_helper import get_jobs, get_applications_for_jobs, get_applicants, add_application
from app_pages.view_applicants import build_dataframe, filters, sort_dataframe
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
    
    tab_options = ["Details", "Applications", "Search Applicants"]
    selected_tab = st.radio("Select View", tab_options, horizontal=True, label_visibility="collapsed")

    if selected_tab == "Details":

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

    elif selected_tab == "Applications":
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

    elif selected_tab == "Search Applicants":
        st.subheader("🔍 Search Applicants")

        # 1️⃣ Load all applicants
        with st.spinner("Loading applicants..."):
            apps = get_applicants()
        if not apps:
            st.info("No applicants found.")
            return

        # 2️⃣ Fetch existing applications for this job
        existing_apps = get_applications_for_jobs(job_id)
        applied_ids = {app["applicant_id"] for app in existing_apps.values()}

        # 3️⃣ Filter out applied applicants
        filtered_apps = {aid: data for aid, data in apps.items() if aid not in applied_ids}
        if not filtered_apps:
            st.info("All available applicants have already applied to this job.")
            return
    
        # Build DataFrame
        with st.spinner("Building applicant data..."):
            app_df = build_dataframe(filtered_apps)
    
        # --- 🧩 Sidebar Filters ---
        with st.spinner("Applying filters..."):
            app_df = filters(app_df)
            app_df = sort_dataframe(app_df)

        # Add a 'Select' column for user checkboxes
        app_df["Select"] = False

        # Display toolbar with Select All
        st.header(f"👥 Applicants ({len(app_df)})")
        if st.button("✅ Select All"):
            app_df["Select"] = True

        # Render in editable table
        edited_df = st.data_editor(
            app_df,
            use_container_width=True,
            height=min((len(app_df) + 1) * 35 + 5, 800),
            hide_index=True,
            column_config={
                "Details": st.column_config.LinkColumn(
                    label="Details", help="Click to view applicant details", display_text="View"
                ),
                "Select": st.column_config.CheckboxColumn(
                    label="✔️ Select", help="Select this applicant"
                ),
            },
            disabled=[col for col in app_df.columns if col not in ("Select",)],
        )
        
        if st.button("➕ Create Application(s)"):
            selected = edited_df[edited_df["Select"]]
            if selected.empty:
                st.warning("⚠️ No applicants selected.")
            else:
                success_count = 0
                for _, row in selected.iterrows():
                    applicant_id = row["UUID"]
                    try:
                        add_application(job_id, applicant_id)
                        success_count += 1
                    except Exception as e:
                        st.error(f"Error adding application for {applicant_id}: {e}")
                st.success(f"✅ {success_count} applicant(s) applied to job.")
