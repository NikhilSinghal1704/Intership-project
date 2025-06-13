import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid
import mimetypes
import os


def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("/home/nik/Projects/Intership project/utils/cred.json")
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

def add_job(data, new_skills=None):
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

# Get Functions

def get_open_jobs():
    ref = db.reference("jobs")
    jobs = ref.order_by_child("status").equal_to("open").get()
    return jobs or {}  # returns a dict of {job_id: job_data}

def get_applicants():
    ref = db.reference("applicants")
    return ref.get() or {}  # returns {applicant_id: data}

def get_skills():
    """
    Fetch the list of skills from the Realtime Database.
    """
    ref = db.reference("skills")
    skills = ref.get()
    return skills if isinstance(skills, list) else []

