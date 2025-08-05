import streamlit as st
from datetime import date
from utils.firebase_helper import add_hired

def app():
    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in.")
        st.stop()

    # Read query parameters
    params = st.query_params
    job_id = params.get("job_id")
    applicant_id = params.get("applicant_id")
    application_id = params.get("application_id")

    st.title("📄 Hired Applicant Record")

    if not job_id or not applicant_id or not application_id:
        st.warning("Missing required parameters in URL.")
        st.stop()

    with st.form("hired_applicant_form"):
        st.subheader("🔒 Linked Information (Non-editable)")
        st.text_input("Job ID", value=job_id, disabled=True)
        st.text_input("Applicant ID", value=applicant_id, disabled=True)
        st.text_input("Application ID", value=application_id, disabled=True)

        st.subheader("📌 Hiring Details")

        hired_on = st.date_input("Date of Hire", value=date.today())
        joining_date = st.date_input("Joining Date")
        offered_ctc = st.number_input("Offered CTC (INR)", min_value=0.0, step=1000.0)
        notice_period = st.number_input("Notice Period (days)", min_value=0, step=1)

        status = st.selectbox("Status", ["Joined", "Declined", "Delayed", "On Hold"])
        comments = st.text_area("Comments / Notes", placeholder="Optional notes from HR or recruiter...")

        submitted = st.form_submit_button("📥 Save Hired Record")

        if submitted:
            hired_data = {
                "job_id": job_id,
                "applicant_id": applicant_id,
                "application_id": application_id,
                "hired_on": hired_on.isoformat(),
                "joining_date": joining_date.isoformat(),
                "offered_ctc": offered_ctc,
                "notice_period_days": notice_period,
                "status": status,
                "comments": comments,
            }

            add_hired(hired_data)
            st.success("✅ Hired record saved successfully!")
            redirect_url = f"/view_hired"
            st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}" />', unsafe_allow_html=True)