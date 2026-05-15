import uuid


def add_connection_request(
    connection_requests: list,
    student_name: str,
    student_email: str,
    student_school: str,
    student_major: str,
    advisor_name: str,
    advisor_email: str,
    advisor_company: str,
    notes: str,
) -> None:
    connection_requests.append(
        {
            "request_id": str(uuid.uuid4()),
            "student_email": student_email.strip(),
            "student_name": student_name.strip(),
            "student_school": student_school.strip(),
            "student_major": student_major.strip(),
            "advisor_email": advisor_email.strip(),
            "advisor_name": advisor_name.strip(),
            "advisor_company": advisor_company.strip(),
            "status": "Pending",
            "notes": notes.strip(),
            "advisor_note": "",
        }
    )


def get_advisor_options(users: list) -> list:
    return [
        f"{advisor['full_name']} - {advisor.get('company', '')}"
        for advisor in users
        if advisor.get("role", "").strip().lower() == "advisor"
    ]


def find_advisor_by_label(users: list, selected_advisor: str) -> dict:
    advisor_name, advisor_company = selected_advisor.split(" - ", 1)
    return next(
        (
            advisor
            for advisor in users
            if advisor.get("full_name") == advisor_name
            and advisor.get("company", "") == advisor_company
        ),
        None,
    )
