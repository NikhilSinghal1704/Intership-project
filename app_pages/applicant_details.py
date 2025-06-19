import streamlit as st
from utils.firebase_helper import get_applicants, get_applications_for_applicant, delete_applicant

def app():
    uid = st.query_params.get("uid", [None])
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
        else:
            for app_id, app_data in apps.items():
                st.markdown(f"- **{app_data['job_id']}** (ID: {app_id}) — Status: {app_data.get('status')}")

    with tabs[2]:
        st.subheader("⚠️ Delete Applicant")
        if st.button("Delete Applicant"):
            delete_applicant(uid)  # you need to implement this
            st.success("Applicant deleted.")
            st.experimental_set_query_params()  # clear URL
