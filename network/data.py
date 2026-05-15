from pathlib import Path
import json

json_users = Path("users.json")
json_connections = Path("connection_requests.json")
json_AI_EMAIL = Path("email_context.json")
json_logs = Path("logs.json")
json_resumes = Path("resumes")

users = [
    {
        "id": "1",
        "email": "emdesmo@udel.edu",
        "full_name": "Emily Desmond",
        "password": "testing123",
        "role": "Student",
        "school": "University of Delaware",
        "major": "Management Information Systems",
        "grad_year": 2026,
    },
    {
        "id": "2",
        "email": "joedoe@udel.edu",
        "full_name": "Joe Doe",
        "password": "testing123",
        "role": "Advisor",
        "company": "Tech Solutions",
        "position": "Senior Software Engineer",
    },
]

connections = [
    {
        "request_id": "011101",
        "status": "Pending",
        "advisor_email": "joedoe@udel.edu",
        "advisor_name": "Joe Doe",
        "advisor_company": "Tech Solutions",
        "student_email": "emdesmo@udel.edu",
        "student_name": "Emily Desmond",
        "student_school": "University of Delaware",
        "student_major": "Management Information Systems",
        "notes": "I would love to hear about your experience in the tech industry and any advice you have for someone starting out.",
        "advisor_note": "",
    }
]

ai_email_context = []
logs = []

json_resumes.mkdir(exist_ok=True)


def save_resume(uploaded_file, user_email):
    if uploaded_file is not None:
        file_path = json_resumes / f"{user_email}.pdf"

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return str(file_path)

    return None

def load_data(json_path: Path, default_data: list) -> list:
    if json_path.exists() and json_path.stat().st_size > 0:

        with open(json_path, "r", encoding="utf-8") as f:

            return json.load(f)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(default_data, f, indent=4)

    return default_data.copy()

def save_data(data: list, json_path: Path) -> None:
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

