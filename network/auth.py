import uuid


def create_account(users: list, full_name: str, email: str, password: str, role: str):
    existing_emails = [user.get("email", "").strip().lower() for user in users]

    if email.strip().lower() in existing_emails:
        return None

    new_user = {
        "id": str(uuid.uuid4()),
        "email": email.strip(),
        "full_name": full_name.strip(),
        "password": password,
        "role": role,
    }
    users.append(new_user)
    return new_user


def authenticate_user(users: list, email: str, password: str):
    return next(
        (
            user
            for user in users
            if user.get("email", "").strip().lower() == email.strip().lower()
            and user.get("password") == password
        ),
        None,
    )


def update_profile(
    users: list,
    current_email: str,
    full_name: str,
    email: str,
    school: str = "",
    major: str = "",
    company: str = "",
    position: str = "",
    about: str = "",
):
    for user in users:
        if user.get("email", "").strip().lower() == current_email.strip().lower():
            user["full_name"] = full_name.strip()
            user["email"] = email.strip()
            user["school"] = school.strip()
            user["major"] = major.strip()
            user["company"] = company.strip()
            user["position"] = position.strip()
            user["about"] = about.strip()
            return user

    return None