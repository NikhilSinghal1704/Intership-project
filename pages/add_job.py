import streamlit as st
from utils.firebase_helper import get_skills, add_job

def app():

    #st.set_page_config(page_title="Add Job", page_icon="💼", layout="wide")

    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in to view this page.")
        st.stop()

    st.title("📌 Add New Job Opening")

    existing_skills = get_skills()

    with st.form("job_form"):
        col1, col2 = st.columns(2)

        with col1:
            job_title = st.text_input("Job Title *")
            department = st.text_input("Department")
            location = st.text_input("Job Location")
            work_mode = st.selectbox("Work Mode", ["Onsite", "Remote", "Hybrid"])
            Vacancies = st.number_input("Vacancies *", min_value=1, step=1)

        with col2:
            experience_required = st.number_input("Experience Required (years)", min_value=0.0, step=0.5)
            Budget = st.text_input("Salary Range (Annual CTC)")
            required_skills = st.multiselect(
                "Required Skills *",
                options=existing_skills,
                help="Select or type to add new.",
                accept_new_options=True
            )
            posted_by = st.text_input("Posted By (Email) *")

        st.subheader("Hiring Process")
        stages_input = st.text_input(
            "Stages (comma-separated, in order)",
            placeholder="e.g. Sourcing, Screening, Interview, Offer, Onboarding"
        )

        st.subheader("Job Description")
        description = st.text_area("Describe the role/responsibilities", height=150)

        submitted = st.form_submit_button("➕ Add Job Opening")

        if submitted:
            # Validation
            required = [job_title, posted_by, required_skills, Vacancies]
            if not all(required):
                st.warning("Please complete all required fields marked with *.")
            else:
                # Parse stages
                stages = [s.strip() for s in stages_input.split(",") if s.strip()]
                job_data = {
                    "job_title": job_title,
                    "department": department,
                    "location": location,
                    "work_mode": work_mode,
                    "experience_required": experience_required,
                    "Budget": Budget,
                    "Vacancies": int(Vacancies),
                    "skills": required_skills,
                    "hiring_process": stages,
                    "description": description,
                    "posted_by": posted_by,
                    "Status": "Open",
                }

                # Determine new skills
                new_skills = set(required_skills) - set(existing_skills)

                # Add job
                add_job(job_data, list(new_skills))
                st.success("✅ Job opening added successfully!")
                st.rerun()
