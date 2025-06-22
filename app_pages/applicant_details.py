import streamlit as st
from utils.firebase_helper import get_applicants, get_applications_for_applicant, delete_applicant, get_jobs, update_application_status, delete_application, reject_application


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
    if current == "hired":
        st.markdown("✅ **Applicant has been hired!**")
        if st.button("🗑️ Delete", key=f"del_{app_id}"):
            delete_application(app_id)
            st.rerun()
        st.markdown("---")
        return
    render_stepper(stages, current)
    if rejected:
        st.markdown("❌ **Applicant has been rejected.**")
    col1, col2, col3 = st.columns([1, 1, 1])
    if not rejected:
        if col1.button("➡️ Advance", key=f"adv_{app_id}"):
            next_idx = min(stages.index(current) + 1, len(stages) - 1)
            update_application_status(app_id, stages[next_idx])
            st.rerun()
        if col2.button("❌ Reject", key=f"rej_{app_id}"):
            reject_application(app_id, "true")
            st.rerun()
    else:
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
    uid = st.query_params.get("uid", None)
    if not uid:
        st.info("Select an applicant from the list.")
        return
    data = get_applicants([uid]).get(uid)
    if not data:
        st.error(f"Applicant not found: {uid}")
        return

    tabs = st.tabs(["Details", "Applications", "Delete"])
    with tabs[0]:
        st.subheader("👤 Applicant Details")
        st.write(f"**Name:** {data['name']}")
        st.write(f"**Email:** {data['email']}")
        st.write(f"**Phone:** {data['phone']}")
        st.write(f"**Skills:** {', '.join(data.get('skills', []))}")
        st.write(f"**Education:** {data.get('education')} / {data.get('institute')}")
        st.write(f"**Experience:** {data.get('experience')} years, CTC: {data.get('ctc')}")
        st.write(f"**Location:** {data.get('location')}, Mode: {data.get('work_mode')}")
        st.write(f"**Resume:** {data.get('resume_url')}")

    with tabs[1]:
        st.subheader("📄 Applications")
        apps = get_applications_for_applicant(uid)
        if not apps:
            st.write("No applications found.")
            return

        # Render all application cards
        for aid, ad in apps.items():
            render_app_card(aid, ad)


    with tabs[2]:
        st.subheader("⚠️ Delete Applicant")
        if st.button("Delete Applicant"):
            delete_applicant(uid)  # you need to implement this
            st.success("Applicant deleted.")
            st.experimental_set_query_params()  # clear URL
