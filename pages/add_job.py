import streamlit as st
from utils.firebase_helper import get_skills, add_job

def app():

    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in to view this page.")
        st.stop()

    st.title("📌 Add New Job Opening")

    db = st.session_state.db
    existing_skills = get_skills()

    with st.form("job_opening_form"):
        st.subheader("Job Details")
        job_title = st.text_input("Job Title", placeholder="e.g. Software Engineer")
        department = st.text_input("Department", placeholder="e.g. Engineering")
        location = st.text_input("Job Location", placeholder="e.g. Bangalore / Remote")

        work_mode = st.selectbox("Work Mode", ["Onsite", "Remote", "Hybrid"])
        experience_required = st.number_input("Experience Required (in years)", min_value=0.0, step=0.5)
        Budget = st.text_input("Salary Range (Annual CTC)", placeholder="e.g. 6-12 LPA")

        required_skills = st.multiselect(
            "Required Skills",
            options=existing_skills,
            help="Select required skills. Type to add new.",
            accept_new_options=True
        )

        Vacancies = st.number_input("No. of Vacancies", min_value=0.0, step=1.0)

        description = st.text_area("Job Description", height=200)

        posted_by = st.text_input("Posted By (Email)")

        submitted = st.form_submit_button("Add Job Opening")

        if submitted:
            if not job_title or not posted_by or not required_skills:
                st.warning("Please fill in all required fields (Job Title, Poster Email, Skills).")
            else:

                job_data = {
                    "job_title": job_title,
                    "department": department,
                    "location": location,
                    "work_mode": work_mode,
                    "experience_required": experience_required,
                    "Budget": Budget,
                    "Vacancies": Vacancies,
                    "skills": required_skills,
                    "description": description,
                    "posted_by": posted_by,
                }

                new_skills = set(required_skills) - set(existing_skills)

                # Add job opening to Firestore
                add_job(job_data, new_skills)

                st.success("✅ Job opening added successfully!")
