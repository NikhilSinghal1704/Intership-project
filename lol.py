import random
from utils.firebase_helper import add_job, init_firebase, add_applicant

def get_dummy_jobs(n):
    """
    Returns 'n' dummy job postings covering all fields:
    job_title, department, location, work_mode, experience_required,
    budget, vacancies, skills, hiring_process, description,
    responsibilities, benefits, qualifications, client, contact_person,
    contact, posted_by, status
    """
    clients = ["Acme Corp", "Globex Inc", "Soylent LLC", "Initech", "Umbrella Corp", "Hooli", "Stark Industries", "Wayne Enterprises", "Dunder Mifflin", "Pied Piper"]
    skills = ["Python", "SQL", "Project Management", "Communication", "Leadership", "JavaScript", "React", "Node.js", "Docker", "Kubernetes", "AWS", "Azure", "Machine Learning", "Data Analysis", "Cybersecurity"]
    experience = [x * 0.5 for x in range(0, 11, 1)]  # in years
    vacancies = [1, 2, 3, 4, 5]
    work_modes = ["Onsite", "Remote", "Hybrid"]

    dummy_jobs = []
    for _ in range(n):
        stages = ["applied", "Screening", "Technical Interview", "Offer", "hired"]

        dummy_jobs.append({
            "job_title": f"Software Engineer",
            "department": "Engineering",
            "location": "Bangalore, India",
            "work_mode": random.choice(work_modes),
            "experience_required": round(random.choice(experience),1),
            "budget": "8-12 LPA",
            "vacancies": random.choice(vacancies),
            "skills": random.sample(skills, k=random.randint(2, 5)),
            "hiring_process": stages,
            "description": "Design, develop, and maintain scalable backend services.",
            "responsibilities": (
                "Write clean code, review PRs, mentor juniors, and ensure system reliability."
            ),
            "benefits": (
                "Health insurance, flexible hours, annual bonus, stock options."
            ),
            "qualifications": "B.Tech in Computer Science or related field",
            "client": random.choice(clients),
            "contact_person": "HR Team",
            "contact": "hr@example.com",
            "posted_by": "recruiter@example.com",
            "status": "open",
        })

    return dummy_jobs

import string

def create_dummy_applicant():
    COUNTRY_CODES = {"India": "+91"}
    country_code = random.choice(list(COUNTRY_CODES.keys()))

    name = random.choice(["Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona"])
    phone = ''.join(random.choices(string.digits, k=10))
    email = f"{name.lower()}{random.randint(100,999)}@example.com"
    course = random.choice(["B.Tech", "M.Tech", "B.Sc", "MBA", "BCA"])
    specialization = random.choice(["Computer Science", "Mechanical", "Finance", "AI", "Marketing"])
    institute = random.choice(["IIT Delhi", "NIT Trichy", "IIM Bangalore", "BITS Pilani", "Anna University"])

    skill_pool = ["Python", "JavaScript", "SQL", "React", "Node.js", "AWS", "Docker"]
    skill_yoe_map = {skill: round(random.uniform(0.5, 5.0), 1) for skill in random.sample(skill_pool, k=3)}
    new_skills = skill_yoe_map.keys()

    City = random.choice(["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad"])
    State = random.choice(["Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "Telangana"])
    Country = country_code

    current_mode = random.choice(["Remote", "Onsite", "Hybrid"])
    current_dur = random.choice(["Full Time", "Contractual"])
    preferred_mode = random.choice(["Remote", "Onsite", "Hybrid"])
    preferred_dur = random.choice(["Full Time", "Contractual"])
    source = random.choice(["Job Site", "Referral", "Social Media"])
    total_exp = round(random.uniform(0.5, 10.0), 1)
    final_notice_period = random.choice(["Immediate", "1 Month", "2 Months", "3 Months"])
    ctc = random.randint(3, 25) * 100000

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
    }, list(new_skills))


# Example usage:
if __name__ == "__main__":
    init_firebase()
    '''for job in get_dummy_jobs(16):
        print(job, "\n")
        add_job(job, new_skills=job["skills"], client=job["client"])'''
    
    for applicant in [create_dummy_applicant() for _ in range(10)]:
        print(applicant[0], "\n")
        add_applicant(applicant[0], None, new_skills=list(applicant[1]))
