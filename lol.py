import random
from utils.firebase_helper import add_job, init_firebase

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

# Example usage:
if __name__ == "__main__":
    init_firebase()
    for job in get_dummy_jobs(16):
        print(job, "\n")
        add_job(job, new_skills=job["skills"], client=job["client"])
