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
        job_data = render_job_form(existing_skills, existing_clients)
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
                job_data["hiring_process"] = ["applied"] + stages + ["selected", "offered"]

                # Remove raw input key if it exists
                job_data.pop("hiring_process_raw", None)

                new_skills = set(job_data["skills"]) - set(existing_skills)
                
                add_job(job_data, list(new_skills), job_data["client"])
                st.session_state["show_success_popup"] = True

    if st.session_state.get("show_success_popup", False):
        st.success("✅ Job opening added successfully!")
        if st.button("OK"):
            st.session_state["show_success_popup"] = False
            redirect_url = f"/add_job"
            st.markdown(f'<meta http-equiv="refresh" content="0; url={redirect_url}" />', unsafe_allow_html=True)
            st.rerun()


def render_job_form(existing_skills, existing_clients, job_data=None):
    st.markdown("## 📝 Job Information")

    job_data = job_data or {}

    # --- Section 1: Core Info ---
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("📌 Job Title *", value=job_data.get("job_title", ""))
            department = st.text_input("🏢 Department", value=job_data.get("department", ""))
            location = st.text_input("📍 Job Location", value=job_data.get("location", ""))
            work_mode = st.selectbox(
                "🧭 Work Mode *", 
                options=["Onsite", "Remote", "Hybrid"], 
                index=["Onsite", "Remote", "Hybrid"].index(job_data.get("work_mode", "Onsite"))
            )
            vacancies = st.number_input(
                "👥 Vacancies *", 
                min_value=1, 
                step=1,
                value=job_data.get("vacancies", 1)
            )

        with col2:
            client = st.selectbox(
                "🤝 Client Name (if applicable)",
                options=existing_clients,
                index=existing_clients.index(job_data["client"]) if job_data.get("client") in existing_clients else 0,
                help="Select or type to add a new client.",
                accept_new_options=True
            )
            experience_required = st.number_input(
                "💼 Experience Required (years)", 
                min_value=0.0, 
                step=0.5, 
                value=job_data.get("experience_required", 0.0)
            )
            qualifications = st.text_input("🎓 Qualifications", value=job_data.get("qualifications", ""))
            budget = st.text_input("💰 Salary Range (Annual CTC)", value=job_data.get("budget", ""))
            posted_by = st.text_input("📧 Posted By (Email) *", value=job_data.get("posted_by", ""))

    st.divider()

    # --- Section 2: Contact Info (Optional) ---
    with st.expander("📇 Contact Person (Optional)"):
        col1, col2 = st.columns(2)
        with col1:
            contact_person = st.text_input("👤 Contact Person", value=job_data.get("contact_person", ""))
        with col2:
            contact = st.text_input("📞 Contact Information", value=job_data.get("contact", ""))

    st.divider()

    # --- Section 3: Skills & Hiring Process ---
    st.markdown("## 🛠️ Skills & Process")

    required_skills = st.multiselect(
        "✅ Required Skills *",
        options=existing_skills,
        default=job_data.get("skills", []),
        help="Select from existing or add new ones.",
        accept_new_options=True
    )

    stages_input = st.text_input(
        "📈 Stages (comma-separated)",
        value=', '.join(job_data.get("hiring_process", [])),
        placeholder="e.g. Sourcing, Screening, Interview, Offer"
    )

    job_duration = st.selectbox(
        "⏳ Job Duration",
        options=["Full Time", "Contractual (6+6)", "Contractual (1 year )", "Internship"],
        index=["Full Time", "Contractual (6+6)", "Contractual (1 year )", "Internship"].index(
            job_data.get("job_duration", "Full Time")
        ),
        help="Specify job engagement type."
    )

    st.divider()

    # --- Section 4: Job Description ---
    st.markdown("## 🧾 Job Description")

    description = st.text_area("📋 Job Description", height=150, value=job_data.get("description", ""))
    responsibilities = st.text_area("📌 Responsibilities", height=100, value=job_data.get("responsibilities", ""))
    benefits = st.text_area("🎁 Benefits", height=100, value=job_data.get("benefits", ""))

    # --- Return assembled job data ---
    new_job_data = {
        "job_title": job_title,
        "department": department,
        "location": location,
        "work_mode": work_mode,
        "experience_required": experience_required,
        "budget": budget,
        "vacancies": int(vacancies),
        "skills": required_skills,
        "hiring_process_raw": stages_input,
        "job_duration": job_duration,
        "description": description,
        "responsibilities": responsibilities,
        "benefits": benefits,
        "qualifications": qualifications,
        "client": client,
        "contact_person": contact_person,
        "contact": contact,
        "posted_by": posted_by,
        "status": job_data.get("status", "open"),
    }

    return new_job_data




