import streamlit as st
from utils.firebase_helper import get_jobs, get_applications_for_jobs, get_applicants, add_application, update_application_status, get_skills, get_clients, update_job, delete_job, reject_application
from app_pages.view_applicants import build_dataframe, filters, sort_dataframe, search
from app_pages.add_job import render_job_form
from collections import Counter
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
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
    
    tab_options = ["Details", "Applications", "Search Applicants", "Update"]
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
            st.write(f"**Client:** {job.get('client', '-')}")
            st.write(f"**Contact Person:** {job.get('contact_person', '-')} | **Contact:** {job.get('contact', '-')}")
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

        st.subheader("⚠️ Delete Job")
        st.warning("This action will permanently delete the Job and all associated applications.")
        
        # First confirmation step
        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False
        
        # Step 1: User clicks Delete button
        if not st.session_state.confirm_delete:
            if st.button("🗑️ Delete Job"):
                st.session_state.confirm_delete = True
                st.toast("Please confirm deletion", icon="❗")
        
        # Step 2: Show confirmation buttons
        if st.session_state.confirm_delete:
            st.error("Are you absolutely sure you want to delete this Job?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete"):
                    delete_job(job['id'])  # Your existing function
                    st.success("✅ Job deleted successfully.")
                    st.query_params.clear()
                    st.toast("Redirecting...", icon="🔁")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state.confirm_delete = False
                    st.info("Deletion cancelled.")

    elif selected_tab == "Applications":
        st.subheader("📊 Applications Overview")

        apps = get_applications_for_jobs(job_id)
        if not apps:
            st.info("No applications found for this job.")
            return
        
        stages = job["hiring_process"]

        stage_counts = {}

        for app in apps.values():
            if "status" not in app:
                app["status"] = "applied"

            stage = app["status"]
            index = stages.index(stage)
            #print(index, stage, stages)

            for i in range(index + 1):
                stage_counts[stages[i]] = stage_counts.get(stages[i], 0) + 1
        
        counts = [stage_counts.get(stage, 0) for stage in stages]

        fig = go.Figure(go.Funnel(
            y=stages,
            x=counts,
            textposition="inside",
            textinfo="value",
            opacity=0.7,
            marker=dict(line=dict(width=1, color="white"))
        ))

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        st.subheader("📋 Application List")
        uids = {app["applicant_id"] : app["id"] for app in apps.values()}
        # Build full DataFrame with all parameters
        with st.spinner("Building applicant data..."):
            df_all = build_dataframe(get_applicants(uids.keys()))
        # Use sidebar radio to select stage
        stages = job.get("hiring_process", []) + ['hired']
        selected_stage = st.sidebar.radio("Filter by Stage", options=["All"] + stages + ["rejected"], index=0)

        status_map = {app_data["applicant_id"]: app_data.get("status", "applied") for app_data in apps.values()}
        rejected_map = {app_data["applicant_id"]: str(app_data.get("rejected", "false")) for app_data in apps.values()}
        df_all["Status"] = df_all["UUID"].map(status_map).fillna("-")
        df_all["rejected"] = df_all["UUID"].map(rejected_map).fillna("false")

        # Filter DataFrame based on radio selection
        if selected_stage == "rejected":
            df = df_all[df_all['rejected'] == 'true']
        elif selected_stage != "All":
            df = df_all[df_all["Status"] == selected_stage]
        else:
            df = df_all[(df_all["Status"] != 'hired') & (df_all["rejected"] != "true")]

        # Add a 'Select' column for user checkboxes
        df["Select"] = False

        # Display toolbar with Select All

        df = search(df)
        
        # Ensure 'Select' column exists
        if "Select" not in df.columns:
            df["Select"] = False
        
        # Header
        st.header(f"👥 Applicants ({len(df)})")
        
        # UI
        st.write(f"Showing {len(df)} applicant(s) in stage: **{selected_stage}**")
        
        n_rows = len(df)
        height = min((n_rows + 1) * 35 + 5, 800)
        
        # Data editor
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            height=height,
            hide_index=True,
            column_config={
                "Details": st.column_config.LinkColumn(
                    label="Details",
                    help="Click to view applicant details",
                    display_text="View"
                ),
                "Resume": st.column_config.LinkColumn(
                    label="Resume",
                    help="Click to view resume",
                    display_text="View Resume"
                ),
                "Select": st.column_config.CheckboxColumn(
                    label="✔️ Select", help="Select this applicant"
                ),
            },
        )

        if selected_stage != "hired":        
            # Initialize confirmation flag in session_state
            if "confirm_advance" not in st.session_state:
                st.session_state.confirm_advance = False

            # Step 1: User clicks the initial button
            if not st.session_state.confirm_advance:
                if st.button("🚀 Advance Application(s)"):
                    selected = edited_df[edited_df["Select"]]
                    if selected.empty:
                        st.warning("⚠️ No applicants selected.")
                    else:
                        st.session_state.selected_to_advance = selected  # Store selected in session
                        st.session_state.confirm_advance = True
                        st.toast("Please confirm advancement", icon="❗")

            # Step 2: Show confirmation dialog
            if st.session_state.confirm_advance:
                st.info("Are you sure you want to advance the selected application(s)?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Advance"):
                        success_count = 0
                        for _, row in st.session_state.selected_to_advance.iterrows():
                            applicant_id = row["UUID"]
                            try:
                                current = row["Status"]
                                next_idx = min(stages.index(current) + 1, len(stages) - 1)
                                if selected_stage == "rejected":
                                    reject_application(uids[applicant_id], "false")
                                update_application_status(uids[applicant_id], stages[next_idx])
                                success_count += 1
                            except Exception as e:
                                st.error(f"Error updating application for {applicant_id}: {e}")
                        st.success(f"✅ {success_count} applicant(s) advanced.")
                        st.session_state.confirm_advance = False
                        del st.session_state.selected_to_advance
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel"):
                        st.session_state.confirm_advance = False
                        del st.session_state.selected_to_advance
                        st.info("Advancement cancelled.")


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

        app_df = search(app_df)

        st.header(f"👥 Applicants ({len(app_df)})")
        app_select_all = False
        if st.button("✅ Select All"):
            app_df["Select"] = True
            app_select_all = True

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
                "Resume": st.column_config.LinkColumn(
                    label="Resume",
                    help="Click to view resume",
                    display_text="View Resume"
                ),
                "Select": st.column_config.CheckboxColumn(
                    label="✔️ Select", help="Select this applicant"
                ),
            },
            disabled=[col for col in app_df.columns if col not in ("Select",)],
        )

        if app_select_all:
            edited_df = app_df
        
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
                st.rerun()

    elif selected_tab == "Update":
        existing_skills = get_skills()
        existing_clients = get_clients()
        
        with st.form("job_form"):
            job_data = render_job_form(existing_skills, existing_clients, job)
            submitted = st.form_submit_button("Submit Job Opening")

            if submitted:
                # Validate required fields
                required_fields = [
                    #job_data["job_title"],
                    #job_data["work_mode"],
                    #job_data["skills"],
                    #job_data["vacancies"]
                ]
                if not all(required_fields):
                    st.warning("Please complete all required fields marked with *.")
                else:
                    # Process stages
                    stages_input = job_data.get("hiring_process_raw", "")
                    stages = [s.strip() for s in stages_input.split(",") if s.strip()]
                    job_data["hiring_process"] = stages

                    # Remove raw input key if it exists
                    job_data.pop("hiring_process_raw", None)

                    new_skills = set(job_data["skills"]) - set(existing_skills)
                    
                    update_job(job["id"], job_data, list(new_skills), job_data["client"])

                    st.success("✅ Job opening added successfully!")
                    st.rerun()
