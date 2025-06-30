import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid
import mimetypes
import os
from dotenv import load_dotenv

load_dotenv()


def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(os.environ.get("cred_file"))
        firebase_admin.initialize_app(cred, {
            "databaseURL" : "https://test-1f76f-default-rtdb.asia-southeast1.firebasedatabase.app/",
            #"storageBucket": "test-1f76f.appspot.com"
        })
    return db.reference("/")


# Add Functions

def add_skills(new_skills):
    """
    Merge and add new skills to the list stored in /skills.
    """
    ref = db.reference("skills")
    existing = ref.get()
    existing_skills = existing if isinstance(existing, list) else []
    
    updated_skills = list(set(existing_skills + new_skills))
    ref.set(updated_skills)

def add_clients(new_clients):
    """
    Merge and add new clients to the list stored in /clients.
    """
    ref = db.reference("clients")
    existing = ref.get()
    existing_clients = existing if isinstance(existing, list) else []
    
    updated_clients = list(set(existing_clients + new_clients))
    ref.set(updated_clients)

def add_education(course, specialization):

    course = course.strip()
    specialization = specialization.strip()

    if not course or not specialization:
        return

    ref = db.reference("education")

    current_data = ref.get() or {}

    if course in current_data:
        existing_specs = current_data[course]
        if specialization not in existing_specs:
            existing_specs.append(specialization)
            ref.child(course).set(existing_specs)
    else:
        ref.child(course).set([specialization])
    

def add_applicant(data, resume, new_skills=None):
    """
    Save applicant data to Firestore and update skills list if new ones are added.
    """
    
    applicant_id = str(uuid.uuid4())
    data["id"] = applicant_id
    data["created_at"] = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()


    if resume:
        resume_url = upload_resume_to_firebase(applicant_id, resume)
        data["resume_url"] = resume_url
    else:
        data["resume_url"] = None

    # Save applicant data
    applicants_ref = db.reference("applicants")
    applicants_ref.child(applicant_id).set(data)

    # Update skills list
    if new_skills:
        add_skills(new_skills)

def upload_resume_to_firebase(applicant_id, file):
    """
    Uploads the resume PDF to Firebase Storage under a folder named 'resumes/{applicant_id}.pdf'
    """
    '''bucket = storage.bucket()
    blob = bucket.blob(f"resumes/{applicant_id}.pdf")
    blob.upload_from_file(file, content_type=mimetypes.guess_type(file.name)[0])
    blob.make_public()  # optional, or use token-based access
    return blob.public_url'''

    resumes_dir = "resumes"
    os.makedirs(resumes_dir, exist_ok=True)

    file_path = os.path.join(resumes_dir, f"{applicant_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    return file_path

def add_job(data, new_skills=None, client=None):
    """
    Save job opening data to Firestore.
    """
    job_id = str(uuid.uuid4())
    data["id"] = job_id
    data["posted_at"] = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()

    jobs_ref = db.reference("jobs")
    jobs_ref.child(job_id).set(data)

    if new_skills:
        add_skills(new_skills)
    if client:
        add_clients([client])

def add_application(job_id, applicant_id):
    applications_ref = db.reference("applications")
    new_id = str(uuid.uuid4())
    applications_ref.child(new_id).set({
        "id": new_id,
        "job_id": job_id,
        "applicant_id": applicant_id,
        "applied_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        "status": "applied",
        "rejected": "false"
    })


# Get Functions

def get_open_jobs():
    ref = db.reference("jobs")
    jobs = ref.order_by_child("status").equal_to("open").get()
    return jobs or {}  # returns a dict of {job_id: job_data}

def get_applicants(uids=None):
    ref = db.reference("applicants")
    all_apps = ref.get() or {}
    if uids:
        return {uid: data for uid, data in all_apps.items() if uid in uids}
    return all_apps

def get_jobs(jobids=None):
    ref = db.reference("jobs")
    all_jobs = ref.get() or {}
    if jobids:
        return {jobid: data for jobid, data in all_jobs.items() if jobid in jobids}
    return all_jobs

def get_applications_for_applicant(uid):
    ref = db.reference("applications")
    apps = ref.order_by_child("applicant_id").equal_to(uid).get()
    return apps or {}

def get_applications_for_jobs(uid):
    ref = db.reference("applications")
    apps = ref.order_by_child("job_id").equal_to(uid).get()
    return apps or {}

def get_skills():
    """
    Fetch the list of skills from the Realtime Database.
    """
    ref = db.reference("skills")
    skills = ref.get()
    return skills if isinstance(skills, list) else []

def get_education():
    """
    Fetch the education courses and specializations from the Realtime Database.
    """
    ref = db.reference("education")
    education = ref.get()
    return education if isinstance(education, dict) else {}

def get_clients():
    """
    Fetch the list of skills from the Realtime Database.
    """
    ref = db.reference("clients")
    clients = ref.get()
    return clients if isinstance(clients, list) else []

def get_vacancies(breakdown=False):
    """
    Compute total vacancies and breakdown by department for open jobs.
    
    Returns:
        total_vacancies (int): sum of vacancies for all open jobs.
        vacancies_by_dept (dict): mapping from department name to total vacancies.
    """
    open_jobs = get_open_jobs()  # uses your existing helper to fetch open jobs dict
    total = 0
    vacancies_by_dept = {}
    vacancies_by_mode = {}
    for job_id, data in open_jobs.items():
        # Treat missing or non-int as 0
        vac = data.get("vacancies", 0) or 0
        try:
            vac = int(vac)
        except (ValueError, TypeError):
            vac = 0
        total += vac
        dept = data.get("department") or "Unknown"
        vacancies_by_dept[dept] = vacancies_by_dept.get(dept, 0) + vac
        mode = data.get("work_mode") or "Unknown"
        vacancies_by_mode[mode] = vacancies_by_mode.get(mode, 0) + vac

    if breakdown:
        return total, vacancies_by_dept, vacancies_by_mode
    return total



# Update Functions

def update_application_status(app_id: str, new_status: str) -> None:
    """
    Update the 'status' field of an application document in Firestore.
    """
    app_ref = db.reference(f"applications/{app_id}/status")
    app_ref.set(new_status)

def reject_application(app_id: str, value: str) -> None:
    """
    Mark an application as rejected by setting 'rejected' to True.
    """
    app_ref = db.reference(f"applications/{app_id}/rejected")
    app_ref.set(value)

# Delete Functions

def delete_applicant(uid):
    """
    Delete an applicant and all their associated applications.
    """
    # Remove the applicant record
    db.reference(f"applicants/{uid}").delete()

    # Find and remove applications linked to this applicant
    apps = get_applications_for_applicant(uid)
    if not apps:
        return
    for app_id in apps:
        delete_application(app_id)

def delete_application(app_id: str) -> None:
    """
    Delete an application document from Firestore by ID.
    """
    db.reference(f"applications/{app_id}").delete()

if __name__ == "__main__":
    init_firebase()
    print(len(get_open_jobs()))
    print(get_vacancies())

