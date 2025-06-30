import streamlit as st
from streamlit_tags import st_tags
from utils.firebase_helper import (
    get_skills, get_education,
    add_education, add_applicant
)

COUNTRY_CODES = {
    "India (+91)": "+91",
    "United States (+1)": "+1",
    "United Kingdom (+44)": "+44",
    "Australia (+61)": "+61",
    "Canada (+1)": "+1",
}

def render_education_fields():
    education_data = get_education()
    courses = sorted(education_data.keys())

    col1, col2 = st.columns(2)
    with col1:
        selected_course = st.selectbox("Course", options=courses + ["Other"], key="course_select")
        if selected_course == "Other":
            selected_course = st.text_input("Enter Course", key="custom_course_input").strip()
    with col2:
        specializations = education_data.get(selected_course, []) if selected_course else []
        selected_specialization = st.selectbox(
            "Specialization",
            options=specializations + ["Other"],
            key="specialization_select"
        )
        if selected_specialization == "Other":
            selected_specialization = st.text_input("Enter Specialization", key="custom_specialization_input").strip()
    return selected_course, selected_specialization

def skill_input():

    existing_skills = get_skills()
    
    selected_skills = st.multiselect(
        "Select or type skills",
        options=existing_skills,
        help="You can select multiple or type your own",
        accept_new_options=True
    )

    skill_yoe_map = {}
    for skill in selected_skills:
        yoe = st.number_input(f"Years of Experience in {skill}", min_value=0.0, step=0.1, key=f"yoe_{skill}")
        skill_yoe_map[skill] = yoe

    # Track and return new skills
    new_skills = list(set(selected_skills) - set(existing_skills))

    return skill_yoe_map, new_skills

def app():
    if not st.session_state.get("logged_in"):
        st.error("🚫 Login required.")
        st.stop()

    # 🔹 PERSONAL & CONTACT DETAILS
    st.header("👤 Personal & Contact Info")
    name = st.text_input("Full Name")
    col1, col2 = st.columns([1, 2])
    with col1:
        country_code = st.selectbox("Country Code", list(COUNTRY_CODES.keys()), index=0)
    with col2:
        phone = st.text_input("Phone Number")
    email = st.text_input("Email Address")

    # 🔹 EDUCATION
    st.header("🎓 Education")
    course, specialization = render_education_fields()
    institute = st.text_input("Institute Name")

    # 🔹 SKILLS WITH EXPERIENCE
    st.header("🛠️ Skills & Experience")
    skill_yoe_map, new_skills = skill_input()

    # 🔹 CURRENT & PREFERRED WORK DETAILS
    st.header("🏢 Work Details & Preferences")
    City = st.text_input("Current City")
    State = st.text_input("Current State")
    Country = st.text_input("Current Country", value="India")

    current_mode = st.selectbox("Current Work Mode", ["Onsite", "Remote", "Hybrid"])
    current_dur = st.selectbox("Current Work Duration", ["Full Time", "Contractual"])
    preferred_mode = st.selectbox("Preferred Work Mode", ["Onsite", "Remote", "Hybrid"])
    preferred_dur = st.selectbox("Preferred Work Duration", ["Full Time", "Contractual"])

    # 🔹 ADDITIONAL
    st.header("📌 Application Details")
    source = st.selectbox("Source", ["Job Site", "Referral", "Social Media"])
    total_exp = st.number_input("Total Years of Experience", min_value=0.0, step=0.1)
    ctc = st.number_input("Annual CTC (INR)", step=1000.0)

    # ⚙️ Resumé + Submit in Form
    with st.form("submit_section"):
        resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        submitted = st.form_submit_button("✅ Submit Application")

        if submitted:
            # Validation
            required = [name, phone, email, skill_yoe_map, course, specialization, institute, resume]
            if not all(required):
                st.warning("Please fill in all required fields.")
            else:
                # Persist new options
                add_education(course, specialization)

                data = {
                    "name": name,
                    "phone": f"{COUNTRY_CODES[country_code]} {phone}",
                    "email": email,
                    "course": course,
                    "specialization": specialization,
                    "institute": institute,
                    "skills": skill_yoe_map,
                    "city": City, "state": State, "country": Country,
                    "current_mode": current_mode,
                    "current_duration": current_dur,
                    "preferred_mode": preferred_mode,
                    "preferred_duration": preferred_dur,
                    "source": source,
                    "experience": total_exp,
                    "ctc": ctc,
                }

                add_applicant(data, resume, new_skills=new_skills)
                st.success("✅ Applicant added successfully!")
                st.rerun()
