import streamlit as st
from utils.firebase_helper import get_skills, add_job, get_clients

def app():
    if not st.session_state.get("logged_in", False):
        st.error("🚫 You must be logged in to view this page.")
        st.stop()

    st.markdown("""
    <style>
    .job-form section {
      border: 1px solid #ADD8E6;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      transition: border 0.3s;
    }
    .job-form section:hover {
      border: 2px solid #0D47A1;
    }
    .job-form .stTextInput, .job-form .stTextArea {
      width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("📌 Add New Job Opening")
    existing_skills = get_skills()
    existing_clients = get_clients()

    with st.form("job_form"):
        # Section 1: Core Job Info
        st.markdown('<section class="job-form">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("Job Title *")
            department = st.text_input("Department")
            location = st.text_input("Job Location")
            work_mode = st.selectbox("Work Mode *", ["Onsite", "Remote", "Hybrid"])
            vacancies = st.number_input("Vacancies *", min_value=1, step=1)
            client = st.selectbox(
                "Client Name (if applicable)",
                options=existing_clients,
                help="Select or type to add new.",
                accept_new_options=True
            )
        with col2:
            experience_required = st.number_input(
                "Experience Required (years)", min_value=0.0, step=0.5
            )
            qualifications = st.text_input("Qualifications")
            budget = st.text_input("Salary Range (Annual CTC)")
            contact_person = st.text_input("Contact Person")
            contact = st.text_input("Contact Information")
            posted_by = st.text_input("Posted By (Email) *")
        st.markdown('</section>', unsafe_allow_html=True)

        # Section 2: Skills & Process
        st.markdown('<section class="job-form">', unsafe_allow_html=True)
        required_skills = st.multiselect(
            "Required Skills *",
            options=existing_skills,
            help="Select or type to add new.",
            accept_new_options=True
        )
        stages_input = st.text_input(
            "Stages (comma-separated, in order)",
            placeholder="e.g. Sourcing, Screening, Interview, Offer"
        )
        job_duration = st.selectbox(
            "Job Duration",
            options=["Full Time", "Contractual (6+6)", "Contractual (1 year )", "Internship"],
            help="Select the type of job duration."
        )
        st.markdown('</section>', unsafe_allow_html=True)

        # Section 3: Description & Benefits
        st.markdown('<section class="job-form">', unsafe_allow_html=True)
        description = st.text_area("Job Description", height=150)
        responsibilities = st.text_area("Responsibilities", height=100)
        benefits = st.text_area("Benefits", height=100)
        st.markdown("</section>", unsafe_allow_html=True)

        submitted = st.form_submit_button("Submit Job Opening")

        if submitted:
            required_fields = [job_title, work_mode, required_skills, vacancies]
            if not all(required_fields):
                st.warning("Please complete all required fields marked with *.")
            else:
                # Assemble stages
                stages = [s.strip() for s in stages_input.split(",") if s.strip()]
                stages = ["applied"] + stages + ["selected", "offered"]

                job_data = {
                    "job_title": job_title,
                    "department": department,
                    "location": location,
                    "work_mode": work_mode,
                    "experience_required": experience_required,
                    "budget": budget,
                    "vacancies": int(vacancies),
                    "skills": required_skills,
                    "hiring_process": stages,
                    "job_duration": job_duration,
                    "description": description,
                    "responsibilities": responsibilities,
                    "benefits": benefits,
                    "qualifications": qualifications,
                    "client": client,
                    "contact_person": contact_person,
                    "contact": contact,
                    "posted_by": posted_by,
                    "status": "open",
                }

                new_skills = set(required_skills) - set(existing_skills)
                add_job(job_data, list(new_skills)) if not client else add_job(job_data, list(new_skills), client)
                st.success("✅ Job opening added successfully!")
                st.rerun()
