import streamlit as st
import pandas as pd
from app_pages.add_applicant import form
from utils.firebase_helper import get_applicants, get_applications_for_applicant, delete_applicant, get_jobs, update_application_status, delete_application, reject_application, update_applicant, add_education


def render_stepper(stages: list[str], current_stage: str):
    """
    Renders a horizontal stepper showing stages with markers:
    • Completed ➝ Green
    • Current   ➝ Blue
    • Pending   ➝ Gray
    """
    cols = st.columns(len(stages) * 2 - 1)
    for i, stage in enumerate(stages):
        col = cols[i * 2]
        if stage == current_stage:
            color = "🟦"  # blue square
        elif stages.index(current_stage) > i:
            color = "🟩"  # green square
        else:
            color = "⬜️"  # white square
        col.markdown(f"{color}\n**{stage}**", unsafe_allow_html=True)
        if i < len(stages) -1:
            cols[i*2 +1].markdown("➡️", unsafe_allow_html=True)


def render_app_card(app_id, app_data):
    job_data = get_jobs([app_data["job_id"]]).get(app_data["job_id"], {})
    stages = job_data.get("hiring_process", [])
    current = app_data.get("status", stages[0] if stages else "applied")
    rejected = app_data.get("rejected", "false") == "true"
    st.markdown(f"**Application ID:** {app_id} | **Job:** {job_data.get('job_title','N/A')}")
    render_stepper(stages, current)
        
    col1, col2, col3 = st.columns([1, 1, 1])

    if not rejected:
        if current == "hired":
            if col1.button("Offer Made", key=f"offer_{app_id}"):
                update_application_status(app_id, "offer")
                st.warning("Offer made! Please update the status accordingly.")
                st.rerun()
            if col2.button("❌ Reject", key=f"rej_{app_id}"):
                reject_application(app_id, "true")
                st.rerun()
        else:
            if col1.button("➡️ Advance", key=f"adv_{app_id}"):
                next_idx = min(stages.index(current) + 1, len(stages) - 1)
                update_application_status(app_id, stages[next_idx])
                st.rerun()
            if col2.button("❌ Reject", key=f"rej_{app_id}"):
                reject_application(app_id, "true")
                st.rerun()
    else:
        st.markdown("❌ **Applicant has been rejected.**")
        if col1.button("➡️ Advance anyway", key=f"adv_{app_id}"):
            next_idx = min(stages.index(current) + 1, len(stages) - 1)
            reject_application(app_id, "false")
            update_application_status(app_id, stages[next_idx])
            st.rerun()
        if col2.button("✅ Revert to Applied", key=f"revert_{app_id}"):
            reject_application(app_id, "false")
            update_application_status(app_id, "applied")
            st.rerun()
    if col3.button("🗑️ Delete", key=f"del_{app_id}"):
        delete_application(app_id)
        st.rerun()
    st.markdown("---")


def app():

    # 🛑 Login guard
    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in.")
        st.stop()

    uid = st.query_params.get("uid", None)
    if not uid:
        st.info("Select an applicant from the list.")
        return
    data = get_applicants([uid]).get(uid)
    if not data:
        st.error(f"Applicant not found: {uid}")
        return

    tabs = st.tabs(["Details", "update", "Applications"])
    with tabs[0]:
        st.title(f"👤 {data['name']}")

        # --- Table for top metrics (2 rows, 4 columns) ---

        # Define the labels and values
        personal_details = {
            "📧 Email" : [data.get('email')],
            "📞 Phone" : [data.get('phone')],
            "🏙️ Location" : [f"{data.get('city','')}, {data.get('state','')}, {data.get('country','')}"],
            "⏳ Total Exp (yrs)" : [f"{data.get('experience', 0):.1f}"]
        }
            

        # Build a DataFrame style table with no headers
        df_top = pd.DataFrame(personal_details)
        st.dataframe(df_top, hide_index=True, use_container_width=True)

        st.markdown("---")

        # --- Two-column layout for Education & Skills and Work/Resume ---

        left, right = st.columns(2)

        with left:
            st.subheader("🎓 Education")
            st.write(f"**Course:** {data.get('course', '-')} | **Specialization:** {data.get('specialization', '-')}")
            st.write(f"**Institute:** {data.get('institute', '-')}")
            st.write(f"**Current CTC:** ₹{data.get('ctc', '-'):,}")

            st.markdown("### 🛠️ Skills & Experience")

            # Build skill table: each row "Skill | Years"
            skill_items = data.get("skills", {})
            if skill_items:
                df_skills = pd.DataFrame(
                    [(s, f"{yoe:.1f}") for s, yoe in skill_items.items()],
                    columns=["Skill", "Years"]
                )
                st.dataframe(df_skills, hide_index=True, use_container_width=True)
            else:
                st.write("No skills recorded.")

        with right:
            st.subheader("🏢 Work Details")
            st.write(f"**Current Mode:** {data.get('current_mode','-')} | **Duration:** {data.get('current_duration','-')}")
            st.write(f"**Preferred Mode:** {data.get('preferred_mode','-')} | **Duration:** {data.get('preferred_duration','-')}")
            st.write(f"**Source:** {data.get('source','-')} | **Notice Period:** {data.get('notice_period','-')}")

            st.subheader("📁 Resume")
            resume = data.get("resume_url")
            if resume:
                st.markdown(f"[Download Resume]({resume})")
            else:
                st.write("No resume uploaded.")

        st.markdown("---")

        st.subheader("⚠️ Delete Applicant")
        st.warning("This action will permanently delete the applicant and all associated applications.")

        if st.button("🗑️ Delete Applicant"):
            delete_applicant(uid)  # You said this is implemented
            st.success("✅ Applicant deleted successfully.")

            # Clear query params
            st.query_params.clear()

            # Optional: Small delay or spinner
            st.toast("Redirecting...", icon="🔁")

            # Trigger a rerun to reflect state
            st.rerun()

    with tabs[1]:
        st.subheader("🔧 Update Applicant Details")
        updated_data, new_skills = form(data=data)

        # ⚙️ Resumé + Submit in Form
        with st.form("submit_section"):
            resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
            submitted = st.form_submit_button("✅ Submit Application")

            if submitted:
                # Validation using updated_data
                required = [
                    updated_data.get("name"),
                    updated_data.get("phone"),
                    updated_data.get("email"),
                    updated_data.get("skills"),
                    updated_data.get("course"),
                    updated_data.get("specialization"),
                    updated_data.get("institute"),
                ]
                if not all(required):
                    st.warning("Please fill in all required fields.")
                else:
                    # Persist any new course/specialization
                    add_education(updated_data.get("course"), updated_data.get("specialization"))

                    # Fallback to existing resume URL if no new file uploaded
                    if not resume:
                        updated_data["resume_url"] = data.get("resume_url")

                    update_applicant(uid, updated_data, resume=resume, new_skills=new_skills)
                    st.success("✅ Applicant updated successfully!")
                    st.rerun()

    with tabs[2]:

        st.subheader("📄 Applications")
        apps = get_applications_for_applicant(uid)
        if not apps:
            st.write("No applications found.")
            return

        # Render all application cards
        for aid, ad in apps.items():
            render_app_card(aid, ad)


    
