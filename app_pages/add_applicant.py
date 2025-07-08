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

def render_education_fields(initial_data):
    education_data = get_education()
    courses = sorted(education_data.keys())

    default_course = initial_data.get("course", "")
    default_specialization = initial_data.get("specialization", "")

    col1, col2 = st.columns(2)

    with col1:
        course_options = courses + ["Other"]
        course_index = course_options.index(default_course) if default_course in course_options else len(course_options) - 1
        selected_course = st.selectbox("Course", options=course_options, index=course_index, key="course_select")

        if selected_course == "Other":
            selected_course = st.text_input("Enter Course", value=default_course if default_course not in course_options else "", key="custom_course_input").strip()

    with col2:
        specializations = education_data.get(selected_course, []) if selected_course else []
        specialization_options = specializations + ["Other"]
        specialization_index = specialization_options.index(default_specialization) if default_specialization in specialization_options else len(specialization_options) - 1
        selected_specialization = st.selectbox("Specialization", options=specialization_options, index=specialization_index, key="specialization_select")

        if selected_specialization == "Other":
            selected_specialization = st.text_input("Enter Specialization", value=default_specialization if default_specialization not in specialization_options else "", key="custom_specialization_input").strip()

    return selected_course, selected_specialization


def skill_input(initial_skills_data):
    existing_skills = get_skills()
    
    # Pre-select skills from existing data
    default_selected_skills = list(initial_skills_data.keys()) if initial_skills_data else []

    selected_skills = st.multiselect(
        "Select or type skills",
        options=existing_skills,
        default=default_selected_skills,
        help="You can select multiple or type your own",
        accept_new_options=True,
        key="skill_select"
    )

    skill_yoe_map = {}
    for skill in selected_skills:
        default_yoe = initial_skills_data.get(skill, 0.0)
        yoe = st.number_input(
            f"Years of Experience in {skill}",
            min_value=0.0,
            step=0.1,
            key=f"yoe_{skill}",
            value=default_yoe  # Set initial value from data
        )
        skill_yoe_map[skill] = yoe

    # Detect new skills not in the existing database
    new_skills = list(set(selected_skills) - set(existing_skills))

    return skill_yoe_map, new_skills


def form(data={}):
    # 🔹 PERSONAL & CONTACT DETAILS
    st.header("👤 Personal & Contact Info")
    name = st.text_input("Full Name", value=data.get("name", "") if data else "", placeholder="Enter your full name")

    col1, col2 = st.columns([1, 2])
    with col1:
        default_cc = f"{data.get('phone', '').split()[0]} {data.get('phone', '').split()[1:]}" if data else None
        country_code = st.selectbox(
            "Country Code",
            options=list(COUNTRY_CODES.keys()),
            index=list(COUNTRY_CODES.keys()).index(next(
                (k for k,v in COUNTRY_CODES.items() if v == (data.get("phone","").split()[0] if data else None)),
                list(COUNTRY_CODES.keys())[0]
            ))
        )
    with col2:
        phone = st.text_input(
            "Phone Number",
            value=" ".join(data.get("phone", "").split()[1:]) if data else "",
            placeholder="Enter your phone number without country code"
        )

    email = st.text_input("Email Address", value=data.get("email","") if data else "")

    # 🔹 EDUCATION
    st.header("🎓 Education")
    course, specialization = render_education_fields(data if data else {})
    institute = st.text_input("Institute Name", value=data.get("institute","") if data else "")

    # 🔹 SKILLS WITH EXPERIENCE
    st.header("🛠️ Skills & Experience")
    skill_yoe_map, new_skills = skill_input(data.get("skills") if data else {})


    # 🔹 CURRENT & PREFERRED WORK DETAILS
    st.header("🏢 Work Details & Preferences")
    City = st.text_input("Current City", value=data.get("city","") if data else "")
    State = st.text_input("Current State", value=data.get("state","") if data else "")
    Country = st.text_input("Current Country", value=data.get("country","India") if data else "India")

    current_mode = st.selectbox("Current Work Mode", ["Onsite", "Remote", "Hybrid"], index=["Onsite","Remote","Hybrid"].index(data.get("current_mode","Onsite")) if data else 0)
    current_dur = st.selectbox("Current Work Duration", ["Full Time", "Contractual"], index=["Full Time","Contractual"].index(data.get("current_duration","Full Time")) if data else 0)
    preferred_mode = st.selectbox("Preferred Work Mode", ["Onsite", "Remote", "Hybrid"], index=["Onsite","Remote","Hybrid"].index(data.get("preferred_mode","Onsite")) if data else 0)
    preferred_dur = st.selectbox("Preferred Work Duration", ["Full Time", "Contractual"], index=["Full Time","Contractual"].index(data.get("preferred_duration","Full Time")) if data else 0)

    # 🔹 ADDITIONAL APPLICATION DETAILS
    st.header("📌 Application Details")
    source = st.selectbox("Source", ["Job Site", "Referral", "Social Media"], index=["Job Site","Referral","Social Media"].index(data.get("source","Job Site")) if data else 0)
    total_exp = st.number_input(
        "Total Years of Experience",
        value=float(data.get("experience", 0)),
        min_value=0.0, step=0.1
    )

    notice_vals = ["Immediate", "1 Month", "2 Months", "3 Months", "More than 3 Months"]
    
    # Load stored value
    stored_notice = data.get("notice_period", "Immediate") if data else "Immediate"
    
    # Determine selected value for the selectbox
    selected_notice = stored_notice if stored_notice in notice_vals else "More than 3 Months"
    
    # Selectbox for notice period
    notice_period = st.selectbox(
        "Notice Period",
        options=notice_vals,
        index=notice_vals.index(selected_notice)
    )
    
    # Default value for custom notice
    default_custom_notice = (
        int(stored_notice.split()[0]) if stored_notice not in notice_vals and stored_notice.split()[0].isdigit()
        else 4
    )
    
    # If user selects "More than 3 Months", ask how many months using a number input
    if notice_period == "More than 3 Months":
        months = st.number_input(
            "Enter number of months",
            min_value=4,
            max_value=24,
            value=default_custom_notice,
            step=1
        )
        final_notice_period = f"{months} Months"
    else:
        final_notice_period = notice_period


    ctc = st.number_input(
        "Annual CTC (INR)",
        value=float(data.get("ctc", 0)),
        step=1000.0
    )

    return ({
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
        "notice_period": final_notice_period,
        "ctc": ctc,
    }, new_skills)


def app():
    if not st.session_state.get("logged_in"):
        st.error("🚫 Login required.")
        st.stop()

    data, new_skills = form()

    # ⚙️ Resumé + Submit in Form
    with st.form("submit_section"):
        resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        submitted = st.form_submit_button("✅ Submit Application")

        if submitted:
            # Validation
            required = [data.get("name"), data.get("phone"), data.get("email"), data.get("skills"), data.get("course"), data.get("specialization"), data.get("institute"), resume]
            if not all(required):
                st.warning("Please fill in all required fields.")
            else:
                # Persist new options
                add_education(data.get("course"), data.get("specialization"))


                add_applicant(data, resume, new_skills=new_skills)
                st.success("✅ Applicant added successfully!")
                st.rerun()
