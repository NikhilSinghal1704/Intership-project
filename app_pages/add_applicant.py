import streamlit as st
from streamlit_tags import st_tags
from utils.firebase_helper import get_skills, add_applicant

def app():

    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in to view this page.")
        st.stop()

    st.title("➕ Add New Applicant")

    db = st.session_state.db
    existing_skills = get_skills()

    with st.form("applicant_form"):
        st.subheader("Personal Information")
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")

        st.subheader("Application Source")
        source = st.selectbox(
            "Source Category",
            ["Job Site (Naukri/Indeed)", "Referral", "Social Media (LinkedIn/Other)"]
        )

        st.subheader("Professional Details")

        skills_input = st.multiselect(
            "Skills (select or type to add new)",
            options=existing_skills,
            default=[],
            help="Select existing skills or type a new one and press Enter",
            accept_new_options=True
        )

        education = st.text_input("Education")
        institute = st.text_input("Institute")
        experience = st.number_input("Years of Experience", min_value=0.0, step=0.1)
        ctc = st.number_input("Annual CTC (in INR)", min_value=0.0, step=1000.0)

        st.subheader("Work Details")
        location = st.text_input("Current Location")
        work_mode = st.selectbox("Current Work Mode", ["Onsite", "Remote", "Hybrid"])

        st.subheader("Resume Upload")
        resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

        submitted = st.form_submit_button("Add Applicant")

        if submitted:
            if not name or not phone or not email or not location or not resume_file:
                st.warning("Please fill in all required fields.")
            else:
                data = {
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "source": source,
                    "skills": skills_input,
                    "education": education,
                    "institute": institute,
                    "experience": experience,
                    "ctc": ctc,
                    "location": location,
                    "work_mode": work_mode,
                }

                # Process skills input
                new_skills = list(set(skills_input) - set(existing_skills))
                # Save to Firestore and update skill list
                add_applicant(data, resume_file, new_skills=new_skills)

                st.success("✅ Applicant added successfully!")